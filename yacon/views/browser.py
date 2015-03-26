# yacon.views.browser.py
#
# File Browser Views

import os, logging, json, shutil, operator
from io import FileIO, BufferedWriter
from PIL import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon import conf
from yacon.decorators import verify_node, verify_file_url
from yacon.utils import FileSpec, files_subtree, build_filetree

logger = logging.getLogger(__name__)

# ============================================================================

BUFFER_SIZE = 10485760  # 10MB

# ============================================================================
# Upload Helpers
# ============================================================================

def _upload_save(request, spec):
    """Handles the uploading of a file from the Valum Uploader widget."""
    try:
        if request.is_ajax():
            # using AJAX upload, get the filename out of the query string
            filename = request.GET['qqfile']
            # check that the filename doesn't do anything evil
            if os.path.normpath(filename) != filename:
                logger.error('user sent bad filename: %s', filename)
                raise Http404('bad filename')

            spec.set_filename(filename)

            try:
                os.makedirs(spec.full_dir)
            except OSError:
                pass

            dest = BufferedWriter(FileIO(spec.full_filename, "w"))
            chunk = request.read(BUFFER_SIZE)
            while len(chunk) > 0:
                dest.write(chunk)
                chunk = request.read(BUFFER_SIZE)
        else:
            # not an AJAX request, using iframe method which means there will
            # only be one file at a time, use the first one

            uploaded = request.FILES.values()[0]
            filename = uploaded.name
            spec.set_filename(filename)

            # ??? HAVE TO DO SOMETHING ABOUT THE FILENAME
            # don't forget the normpath check

            dest = BufferedWriter(FileIO(spec.full_filename, "w"))
            for chunk in uploaded.chunks():
                dest.write(chunk)
    except:
        # normally wouldn't use 404 for this kind of error but it allows us to
        # treat it as an exception instead of handling different returns, the
        # widget doesn't care, if it doesn't get back json({success}) is
        # reports an error
        logger.exception('Upload caused exception')
        raise Http404('Upload caused exception')

    return spec


def _handle_upload(request, prefix=None):
    if request.method == 'GET':
        raise Http404('GET not supported for upload_file')

    node = request.GET.get('node')
    if not node:
        raise Http404('No node sent with upload')

    spec = FileSpec(node, prefix=prefix)
    if not spec.allowed_for_user(request.user):
        raise Http404('permission denied')

    _upload_save(request, spec)

    # check if upload had an image extension
    if not spec.extension:
        return spec

    if spec.extension.lower() not in conf.site.image_extensions:
        return spec

    # create thumbnails for the image if configured
    if len(conf.site.auto_thumbnails) == 0:
        return spec

    try:
        for key, value in conf.site.auto_thumbnails['config'].items():
            spec.make_thumbnail(conf.site.auto_thumbnails['dir'], 
                key, value[0], value[1])

    except KeyError, e:
        logger.error(('auto_thumbnails missing conf key stopping thumbnail '
            'generation'), e.message)

    return spec

# ============================================================================
# Browser Views
# ============================================================================

@login_required
def ckeditor_browser(request):
    func_num = request.GET.get('CKEditorFuncNum', None)
    if not func_num:
        raise Http404('CKEditorFuncNum must be provided')

    image_only = request.GET.get('image_only', False)
    if image_only == "1":
        image_only = True

    request.session['func_num'] = func_num
    request.session['choose_mode'] = 'ckeditor'
    request.session['image_only'] = image_only
    request.session['popup'] = True
    data = {
        'title':'Uploads',
        'base_template':'browser_base.html',
        'popup':True,
    }
    return render_to_response('browser/browser.html', data, 
        context_instance=RequestContext(request))


@login_required
def popup_browser(request, callback):
    image_only = request.GET.get('image_only', False)
    if image_only == "1":
        image_only = True

    choose_mode = request.GET.get('choose_mode', 'singleselect')

    request.session['callback'] = callback
    request.session['choose_mode'] = choose_mode
    request.session['image_only'] = image_only
    request.session['popup'] = True
    data = {
        'title':'File Browser',
        'base_template':'browser_base.html',
        'popup':True,
    }
    return render_to_response('browser/browser.html', data, 
        context_instance=RequestContext(request))


# ============================================================================
# Browser Ajax Views
# ============================================================================

@login_required
def root_control(request, tree_type):
    data = {
        'tree_type':tree_type,
        'is_superuser':request.user.is_superuser,
    }
    return render_to_response('browser/root_control.html', data, 
        context_instance=RequestContext(request))


@login_required
@csrf_exempt
def upload_file(request):
    spec = _handle_upload(request)
    return HttpResponse(spec.json_results)


@login_required
@csrf_exempt
def user_upload_file(request):
    prefix = 'users/%s' % request.user.username
    spec = _handle_upload(request, prefix=prefix)
    return HttpResponse(spec.json_results)


@login_required
def tree_top(request):
    expanded = []
    if 'expandedKeyList' in request.GET:
        for key in request.GET['expandedKeyList'].split(','):
            key = key.strip()
            if key:
                expanded.append(key)

    restricted = None
    if not request.user.is_superuser:
        restricted = request.user.username

    try:
        tree = build_filetree(expanded, restricted)
    except OSError:
        tree = ['File error, is MEDIA_ROOT set?']

    return HttpResponse(json.dumps(tree), content_type='application/json')


@login_required
def sub_tree(request):
    key = request.GET.get('key')
    if not key:
        raise Http404('no key sent')

    spec = FileSpec(key)
    tree = files_subtree(spec, 1, [])
    if 'children' in tree:
        subtree = tree['children']
    else:
        subtree = []

    return HttpResponse(json.dumps(subtree), content_type='application/json')


class StubFile(object):
    pass


@login_required
@verify_node('node', False)
def show_folder(request):
    spec = request.spec    # verify_node puts this in the request
    image_only = request.session.get('image_only', False)
    popup = request.session.get('popup', False)
    base_url = settings.MEDIA_URL
    if spec.file_type == 'private':
        base_url = conf.site.private_upload

    relative_url = base_url + spec.relative_dir + '/'

    files = []
    images = []
    for x in os.listdir(spec.full_dir):
        if os.path.isdir(os.path.join(spec.full_dir, x)):
            continue

        stub = StubFile()
        stub.name = x
        stub.lower_name = x.lower()
        pieces = x.split('.')
        stub.ext = ''
        if len(pieces) > 1:
            stub.ext = pieces[-1]

        filename = os.path.join(spec.relative_dir, x)
        stub.url = base_url + filename

        if stub.ext in conf.site.image_extensions:
            images.append(stub)
        else:
            if not image_only:
                files.append(stub)

    images.sort(key=operator.attrgetter('lower_name'))
    files.sort(key=operator.attrgetter('lower_name'))

    data = {
        'title':'Folder Info',
        'node':request.GET['node'],
        'spec':spec,
        'relative_url':relative_url,
        'files':files,
        'images':images,
        'image_extensions':json.dumps(conf.site.image_extensions),
        'func_num':request.session.get('func_num', None),
        'choose_mode':request.session.get('choose_mode', 'view'),
        'callback':request.session.get('callback', ''),
        'image_only':image_only,
        'popup':popup,
    }

    return render_to_response('browser/show_folder.html', data, 
        context_instance=RequestContext(request))


@login_required
@verify_node('node', False)
def add_folder(request, name):
    spec = request.spec    # verify_node puts this in the request
    dir_path = os.path.join(spec.full_dir, name)
    os.mkdir(dir_path)

    return HttpResponse()


@login_required
@verify_node('node', False)
def remove_folder_warn(request):
    """Ajax call that returns a listing of the directories and files that
    would be effected if the given folder was removed."""
    spec = request.spec    # verify_node puts this in the request

    files = []
    dirs = []
    for dirpath, dirnames, filenames in os.walk(spec.full_dir):
        for filename in filenames:
            stored_name = os.path.join(spec.relative_dir, filename)
            files.append(stored_name)

        for dirname in dirnames:
            stored_name = os.path.join(spec.relative_dir, dirname)
            dirs.append(stored_name)

    data = {
        'files':files,
        'dirs':dirs,
        'spec':spec,
        'node':request.GET['node'],
    }

    return render_to_response('browser/remove_folder_warning.html', 
        data, context_instance=RequestContext(request))


@login_required
@verify_node('node', False)
def remove_folder(request):
    spec = request.spec    # verify_node puts this in the request
    shutil.rmtree(spec.full_dir)
    return HttpResponse()


@login_required
@verify_node('node', True)
def remove_file(request):
    spec = request.spec    # verify_node puts this in the request
    if not os.path.exists(spec.full_filename):
        logger.error('ignored request to remove non-existent %s',
            spec.full_filename)
        return HttpResponse()

    os.remove(spec.full_filename)

    # search for any matching files with the same name in any thumbnails
    # directories
    if len(conf.site.auto_thumbnails) == 0:
        return HttpResponse()

    try:
        thumb_path = os.path.abspath(os.path.join(spec.full_dir, 
            conf.site.auto_thumbnails['dir']))
        for path, dirs, files in os.walk(thumb_path):
            for filename in files:
                if os.path.basename(filename) == spec.basename:
                    full_filename = os.path.abspath(os.path.join(path, 
                        filename))
                    os.remove(full_filename)

    except KeyError, e:
        logger.error(('auto_thumbnails missing conf key stopping thumbnail '
            'removal'), e.message)

    return HttpResponse()


@login_required
@verify_file_url('image', True)
def image_edit(request):
    data = {
        'spec':request.spec, # verify_file_url puts this in the request
    }
    if not os.path.exists(request.spec.full_filename):
        return render_to_response('browser/image_edit_error.html', data, 
            context_instance=RequestContext(request))

    return render_to_response('browser/image_edit.html', data, 
        context_instance=RequestContext(request))


@login_required
@verify_file_url('image', True)
def image_edit_save(request):
    spec = request.spec
    if not os.path.exists(request.spec.full_filename):
        return HttpResponse('File not found on server', status='404')

    # use PIL to rotate, scale and crop the image
    changed = False
    img = Image.open(spec.full_filename)
    rotate = request.GET.get('rotate')
    if rotate:
        img = img.rotate(-1 * int(rotate))
        changed = True

    width = request.GET.get('scale_width')
    height = request.GET.get('scale_height')
    if width:
        img = img.resize((int(float(width)), int(float(height))), 
            Image.ANTIALIAS)
        changed = True

    x1 = request.GET.get('crop_x1')
    y1 = request.GET.get('crop_y1')
    x2 = request.GET.get('crop_x2')
    y2 = request.GET.get('crop_y2')
    if x1:
        box = (int(float(x1)), int(float(y1)), int(float(x2)), int(float(y2)))
        img = img.crop(box)
        changed = True
        
    if not changed or len(conf.site.auto_thumbnails) == 0:
        return HttpResponse()

    # image changed, saved the new one and update any thumbnails
    img.save(spec.full_filename)
    try:
        for key, value in conf.site.auto_thumbnails['config'].items():
            spec.make_thumbnail(conf.site.auto_thumbnails['dir'], 
                key, value[0], value[1])

    except KeyError, e:
        logger.error(('auto_thumbnails missing conf key stopping thumbnail '
            'generation'), e.message)

    return HttpResponse()
