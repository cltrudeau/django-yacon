# yacon.views.browser.py
#
# File Browser Views

import os, logging, json, urllib, shutil, operator
from io import FileIO, BufferedWriter
from PIL import Image

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon import conf
from yacon.decorators import verify_node
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

    return spec


def _handle_upload_image(request, prefix=None):
    spec = _handle_upload(request, prefix=prefix)

    # create thumbnails for the image if configured
    if len(conf.site.auto_thumbnails) == 0:
        return spec

    try:
        pass

    except KeyError:
        logger.error(('auto_thumbnails missing key "%s" stopping thumbnail '
            'generation'), e.message)

    for key, value in conf.site.auto_thumbnails.items():
        image_dir = os.path.realpath(os.path.join(spec.full_dir, key))
        image_name = os.path.join(image_dir, spec.basename)
        try:
            os.makedirs(image_dir)
        except:
            # already exists, do nothing
            pass

        # use PIL to create the thumbnail
        im = Image.open(spec.full_filename)
        im.thumbnail(value, Image.ANTIALIAS)
        im.save(image_name, 'JPEG')

    return spec

# ============================================================================
# Browser Views
# ============================================================================

@login_required
def ckeditor_browser(request):
    func_num = request.GET.get('CKEditorFuncNum', None)
    if not func_num:
        raise Http404('CKEditorFuncNum must be provided')

    data = {
        'CKEditorFuncNum':func_num,
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
@csrf_exempt
def upload_image(request):
    spec = _handle_upload_image(request)
    return HttpResponse(spec.json_results)


@login_required
@csrf_exempt
def upload_user_image(request):
    prefix = 'users/%s' % request.user.username
    spec = _handle_upload_image(request, prefix=prefix)
    return HttpResponse(spec.json_results)


@login_required
def tree_top(request):
    expanded = []
    if 'expandedKeyList' in request.GET:
        for key in request.GET['expandedKeyList'].split(','):
            key = key.strip()
            if key:
                expanded.append(key)

    tree = build_filetree(expanded)
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
@verify_node(False)
def show_folder(request, node):
    spec = request.spec    # verify_node puts this in the request

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
        if spec.file_type == 'private':
            stub.url = conf.site.private_upload + filename
        else:
            stub.url = settings.MEDIA_URL + filename

        if stub.ext in conf.site.image_extensions:



            images.append(stub)
        else:
            files.append(stub)

    images.sort(key=operator.attrgetter('lower_name'))
    files.sort(key=operator.attrgetter('lower_name'))
    data = {
        'title':'Folder Info',
        'node':node,
        'spec':spec,
        'files':files,
        'images':images,
    }

    return render_to_response('browser/show_folder.html', data, 
        context_instance=RequestContext(request))


@login_required
@verify_node(False)
def add_folder(request, node, name):
    spec = request.spec    # verify_node puts this in the request
    dir_path = os.path.join(spec.full_dir, name)
    os.mkdir(dir_path)

    return HttpResponse()


@login_required
@verify_node(False)
def remove_folder_warn(request, node):
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
        'node':node,
    }

    return render_to_response('browser/remove_folder_warning.html', 
        data, context_instance=RequestContext(request))


@login_required
@verify_node(False)
def remove_folder(request, node):
    spec = request.spec    # verify_node puts this in the request
    shutil.rmtree(spec.full_dir)
    return HttpResponse()


@login_required
@verify_node(True)
def remove_file(request, node):
    spec = request.spec    # verify_node puts this in the request
    os.remove(spec.full_filename)

    return HttpResponse()
