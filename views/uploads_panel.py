# yacon.views.uploads.py

import os, logging, json, urllib, shutil
from io import FileIO, BufferedWriter
from PIL import Image

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon import conf
from yacon.decorators import superuser_required
from yacon.models import StoredFile, FileSpec

logger = logging.getLogger(__name__)

# ============================================================================

BUFFER_SIZE = 10485760  # 10MB

# ============================================================================
# Helpers
# ============================================================================

# -------------------
# Dynatree Methods

def _files_subtree(spec, depth_limit, expanded):
    """Returns a hash representation in dynatree format of the public or
    private upload directories."""
    file_hash = {
        'title':spec.title,
        'key':spec.key,
        'icon':'fatcow/folder.png',
        'isLazy':True,
    }

    if depth_limit == 0 and file_hash['key'] not in expanded:
        # reached as far as we're going to go, check for kids
        has_child_directories = False
        for x in os.listdir(spec.full_dir):
            if os.path.isdir(x):
                has_child_directories = True
                break

        if has_child_directories:
            file_hash['isLazy'] = True

        return file_hash

    # process any child directories
    children = []
    for x in os.listdir(spec.full_dir):
        dir_path = os.path.abspath(os.path.join(spec.full_dir, x))
        if os.path.isdir(dir_path):
            dl = depth_limit
            if dl != -1:
                dl = dl - 1

            # if the file_type is system, then convert to what is under it
            # (either public or private), otherwise just add to the parent's
            # key
            if spec.file_type != 'system':
                key = '%s:%s' % (spec.file_type, os.path.join(
                    spec.relative_dir, x))
            else:
                key = '%s:%s' % (spec.basename, x)

            spec2 = FileSpec(key)
            subtree = _files_subtree(spec2, dl, expanded)
            children.append(subtree)

    if children:
        file_hash['children'] = children

    return file_hash


def _build_filetree(expanded):
    """Returns a dynatree hash representation of our public and private file
    directory hierarchy."""
    spec = FileSpec('system:public')
    spec.set_filename('public')
    public_node = {
        'title': 'Public',
        'key': 'system:public',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }
    public = _files_subtree(spec, 2, expanded)
    if 'children' in public:
        public_node['children'] = public['children']
        public['children'][0]['activate'] = True

    spec = FileSpec('system:private')
    spec.set_filename('private')
    private_node = {
        'title': 'Private',
        'key': 'system:private',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }
    private = _files_subtree(spec, 2, expanded)
    if 'children' in private:
        private_node['children'] = private['children']
        private['children'][0]['activate'] = True

    tree = [public_node, private_node]
    return tree

# -------------------
# Upload Methods

def _upload_save(request, spec):
    """Handles the uploading of a file from the Valum Uploader widget."""
    try:
        #import pudb; pudb.set_trace()
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
            except:
                pass

            files = StoredFile.objects.filter(owner=request.user,
                file_field=spec.relative_filename)
            if len(files) != 0:
                files.delete()

            dest = BufferedWriter(FileIO(spec.full_filename, "w"))
            chunk = request.read(BUFFER_SIZE)
            while len(chunk) > 0:
                dest.write(chunk)
                chunk = request.read(BUFFER_SIZE)

            spec.stored = StoredFile.objects.create(owner=request.user,
                file_field=spec.relative_filename, is_private=spec.is_private)
        else:
            # not an AJAX request, using iframe method which means there will
            # only be one file at a time, use the first one

            upload = request.FILES.values()[0]
            filename = upload.name
            spec.set_filename(filename)
            wrapped_file = UploadedFile(upload)

            # ??? HAVE TO DO SOMETHING ABOUT THE FILENAME
            # don't forget the normpath check
            spec.stored = StoredFile.objects.create(file_field=upload,
                owner=request.user)
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
    _upload_save(request, spec)

    return spec


def _handle_upload_image(request, prefix=None):
    spec = _handle_upload(request, prefix=prefix)

    # create thumbnails for the image if configured
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
# Upload Management Tab
# ============================================================================

@superuser_required
def root_control(request, tree_type):
    return render_to_response('nexus/ajax/uploads/root_control.html', {}, 
        context_instance=RequestContext(request))


@superuser_required
@csrf_exempt
def upload_file(request):
    spec = _handle_upload(request)
    return HttpResponse(spec.json_results)


@superuser_required
@csrf_exempt
def user_upload_file(request):
    spec = _handle_upload(request, prefix=request.user.username)
    return HttpResponse(spec.json_results)


@superuser_required
@csrf_exempt
def upload_image(request):
    spec = _handle_upload_image(request)
    return HttpResponse(spec.json_results)


@superuser_required
@csrf_exempt
def upload_user_image(request):
    spec = _handle_upload_image(request, prefix=request.user.username)
    return HttpResponse(spec.json_results)


@superuser_required
def tree_top(request):
    expanded = []
    if 'expandedKeyList' in request.GET:
        for key in request.GET['expandedKeyList'].split(','):
            key = key.strip()
            if key:
                expanded.append(key)

    tree = _build_filetree(expanded)
    return HttpResponse(json.dumps(tree), content_type='application/json')


@superuser_required
def sub_tree(request):
    key = request.GET.get('key')
    if not key:
        raise Http404('no key sent')

    spec = FileSpec(key)
    tree = _files_subtree(spec, 1, [])
    if 'children' in tree:
        subtree = tree['children']
    else:
        subtree = []

    return HttpResponse(json.dumps(subtree), content_type='application/json')


class StubFile(object):
    pass

@superuser_required
def folder_info(request, node):
    spec = FileSpec(node)

    files = []
    for x in os.listdir(spec.full_dir):
        if os.path.isdir(os.path.join(spec.full_dir, x)):
            continue

        stub = StubFile()
        stub.name = x

        # find the StoredFile object for this spec
        filename = os.path.join(spec.relative_dir, x)
        try:
            stored = StoredFile.objects.get(file_field=filename)
            stub.url = stored.file_field.url
        except StoredFile.DoesNotExist:
            stored = None
            if spec.file_type == 'private':
                stub.url = conf.site.private_upload + filename
            else:
                stub.url = settings.MEDIA_URL + filename

        stub.stored = stored
        files.append(stub)

    data = {
        'title':'Folder Info',
        'node':node,
        'spec':spec,
        'files':files,
    }

    return render_to_response('nexus/ajax/uploads/folder_info.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def add_to_database(request, node):
    spec = FileSpec(node, node_is_file=True)

    # check the file exists
    if not os.path.isfile(spec.full_filename):
        raise Http404('no such file')

    try:
        StoredFile.objects.get(file_field=spec.relative_filename)
        # file already exists, do nothing
    except StoredFile.DoesNotExist:
        StoredFile.objects.create(file_field=spec.relative_filename, 
            owner=request.user, is_private=spec.is_private)

    return HttpResponse()


@superuser_required
def add_folder(request, node, name):
    spec = FileSpec(node)
    dir_path = os.path.join(spec.full_dir, name)
    os.mkdir(dir_path)

    return HttpResponse()


@superuser_required
def remove_folder_warn(request, node):
    """Ajax call that returns a listing of the directories and files that
    would be effected if the given folder was removed."""
    spec = FileSpec(node)

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

    return render_to_response('nexus/ajax/uploads/remove_folder_warning.html', 
        data, context_instance=RequestContext(request))


@superuser_required
def remove_folder(request, node):
    spec = FileSpec(node)

    for dirpath, dirnames, filenames in os.walk(spec.full_dir):
        for filename in filenames:
            stored_name = os.path.join(spec.relative_dir, filename)
            try:
                stored = StoredFile.objects.get(file_field=stored_name)
                stored.delete()
            except StoredFile.DoesNotExist:
                # no object, do nothing
                pass

    # all of stored file objects should be gone, now just remove the tree
    shutil.rmtree(spec.full_dir)
    return HttpResponse()


@superuser_required
def list_owners(request):
    users = User.objects.all()
    data = {}
    for user in users:
        data[user.id] = '%s %s (%s)' % (user.first_name, user.last_name, 
            user.username)

    return HttpResponse(json.dumps(data), content_type='application/json')


@superuser_required
def change_owner(request, node, user_id):
    user = get_object_or_404(User, id=user_id)
    spec = FileSpec(node, node_is_file=True)

    try:
        stored = StoredFile.objects.get(file_field=spec.relative_filename)
        stored.owner = user
        stored.save()
    except StoredFile.DoesNotExist:
        # no object, do nothing
        pass

    return HttpResponse()


@superuser_required
def remove_file(request, node):
    spec = FileSpec(node, node_is_file=True)

    # node will have the full file name, so path is everything 
    try:
        stored = StoredFile.objects.get(file_field=spec.relative_filename)
        stored.delete()
    except StoredFile.DoesNotExist:
        # no copy in the database do nothing
        
        pass

    # remove from the filesystem
    os.remove(spec.full_filename)

    return HttpResponse()
