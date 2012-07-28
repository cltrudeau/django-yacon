# yacon.views.uploads.py

import os, logging, json, urllib, shutils
from io import FileIO, BufferedWriter

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon.conf import site
from yacon.decorators import superuser_required
from yacon.models import StoredFile

logger = logging.getLogger(__name__)

# ============================================================================

BUFFER_SIZE = 10485760  # 10MB

# ============================================================================
# Helpers
# ============================================================================

def _full_path(tree_type, path):
    if tree_type == 'public':
        full_path = os.path.join(settings.MEDIA_ROOT, path)
    elif tree_type == 'private' and site('private_upload'):
        full_path = os.path.join(site('private_upload'), path)
    else:
        raise Http404('bad tree type')

    full_path = os.path.abspath(full_path)
    return full_path


def _path_parts(node):
    pieces = node.split(':')
    try:
        path = urllib.unquote(pieces[1])
        full_path = _full_path(pieces[0], path)
    except IndexError:
        raise Http404('bad node key')

    return (path, full_path)


def _files_subtree(tree_type, path, depth_limit, expanded):
    """Returns a hash representation in dynatree format of the public or
    private upload directories."""
    full_path = _full_path(tree_type, path)
    file_hash = {
        'title':os.path.basename(full_path),
        'key':'%s:%s' % (tree_type, path),
        'icon':'fatcow/folder.png',
        'isLazy':True,
    }

    if not path:
        file_hash['expand'] = True

    if depth_limit == 0 and file_hash['key'] not in expanded:
        # reached as far as we're going to go, check for kids
        has_child_directories = False
        for x in os.listdir(full_path):
            if os.path.isdir(x):
                has_child_directories = True
                break

        if has_child_directories:
            file_hash['isLazy'] = True

        return file_hash

    # process any child directories
    children = []
    for x in os.listdir(full_path):
        dir_path = os.path.abspath(os.path.join(full_path, x))
        if os.path.isdir(dir_path):
            dl = depth_limit
            if dl != -1:
                dl = dl - 1
            subtree = _files_subtree(tree_type, os.path.join(path, x), dl, 
                expanded)
            children.append(subtree)

    if children:
        file_hash['children'] = children

    return file_hash


def _build_filetree(expanded):
    """Returns a dynatree hash representation of our public and private file
    directory hierarchy."""
    public_node = {
        'title': 'Public',
        'key': 'system:public',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }
    public = _files_subtree('public', '', 2, expanded)
    if 'children' in public:
        public_node['children'] = public['children']
        public['children'][0]['activate'] = True

    private_node = {
        'title': 'Private',
        'key': 'system:private',
        'expand': True,
        'icon': 'fatcow/folders_explorer.png',
    }
    private = _files_subtree('private', '', 2, expanded)
    if 'children' in private:
        private_node['children'] = private['children']
        private['children'][0]['activate'] = True

    tree = [public_node, private_node]
    return tree

# ============================================================================
# Upload Management Tab
# ============================================================================

@superuser_required
def uploads_tab(request):
    return render_to_response('nexus/uploads/uploader.html', {}, 
        context_instance=RequestContext(request))


@superuser_required
@csrf_exempt
def upload_file(request):
    if request.method == 'GET':
        # return a list of the current files
        results = []
        for file_obj in StoredFile.objects.all():
            results.append(_file_hash(file_obj))

        return JSONResponse(results)

    # else: request == POST
    dest = None
    if request.is_ajax():
        print 'using XHR'
        # using AJAX upload, get the filename out fo the query string
        try:
            filename = request.GET['qqfile']
            path = os.path.join(settings.MEDIA_ROOT, filename)
            try:
                os.makedirs(os.path.realpath(os.path.dirname(path)))
            except:
                pass

            dest = BufferedWriter(FileIO(path, "w"))
            chunk = request.read(BUFFER_SIZE)
            while len(chunk) > 0:
                dest.write(chunk)
                chunk = request.read(BUFFER_SIZE)

            stored = StoredFile.objects.create(file_field=filename)
        except Exception:
            logger.exception('Upload caused exception')
            return HttpResponseBadRequest('File failed to upload')
    else:
        # not an AJAX request, using iframe method which means there will only
        # be one file at a time, use the first one
        try:
            upload = request.FILES.values()[0]
            filename = upload.name
            wrapped_file = UploadedFile(upload)
            stored = StoredFile.objects.create(file_field=upload)
        except:
            return HttpResponseBadRequest('File failed to upload')
            
    results = {
        'success':True,
        'filename':filename,
    }

    return HttpResponse(json.dumps(results))


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

    (tree_type, path) = key.split(':')
    if not tree_type or not path:
        raise Http404('bad key sent: "%s"' % key)

    tree = _files_subtree(tree_type, path, 1, [])
    if 'children' in tree:
        subtree = tree['children']
    else:
        subtree = []
    return HttpResponse(json.dumps(subtree), content_type='application/json')


@superuser_required
def folder_info(request, node):
    path, full_path = _path_parts(node)
    files = []
    for x in os.listdir(full_path):
        if os.path.isdir(os.path.join(full_path, x)):
            continue

        # find the StoredFile object for this path
        filename = os.path.join(path, x)
        try:
            stored = StoredFile.objects.get(file_field=filename)
        except StoredFile.DoesNotExist:
            stored = None

        files.append((x, stored))

    data = {
        'title':'Folder Info',
        'node':node,
        'path':path,
        'files':files,
    }

    return render_to_response('nexus/ajax/folder_info.html', data, 
        context_instance=RequestContext(request))


@superuser_required
def add_to_database(request, node):
    path, full_path = _path_parts(node)

    # check the file exists
    if not os.path.isfile(full_path):
        raise Http404('no such file')

    try:
        StoredFile.objects.get(file_field=path)
        # file already exists, do nothing
    except StoredFile.DoesNotExist:
        StoredFile.objects.create(file_field=path)

    return HttpResponse()


@superuser_required
def add_folder(request, node, name):
    path, full_path = _path_parts(node)
    dir_path = os.path.join(full_path, name)
    os.mkdir(dir_path)

    return HttpResponse()


@superuser_required
def remove_folder_warn(request, node):
    """Ajax call that returns a listing of the directories and files that
    would be effected if the given folder was removed."""
    path, full_path = _path_parts(node)

    files = []
    dirs = []
    for dirpath, dirnames, filenames in os.walk(full_path):
        for filename in filenames:
            stored_name = os.path.join(path, filename)
            try:
                stored = StoredFile.objects.get(file_field=stored_name)
            except StoredFile.DoesNotExist:
                stored = None

            files.append((stored_name, stored))

        for dirname in dirnames:
            stored_name = os.path.join(path, dirname)
            dirs.append(stored_name)

    data = {
        'files':files,
        'dirs':dirs,
    }

    return render_to_response('nexus/ajax/upload_remove_folder_warning.html', 
        data, context_instance=RequestContext(request))


@superuser_required
def remove_folder(request, node):
    path, full_path = _path_parts(node)

    for dirpath, dirnames, filenames in os.walk(full_path):
        for filename in filenames:
            stored_name = os.path.join(path, filename)
            try:
                stored = StoredFile.objects.get(file_field=stored_name)
                stored.delete()
            except StoredFile.DoesNotExist:
                # no object, do nothing
                pass

    # all of stored file objects should be gone, now just remove the tree
    shutils.rmtree(full_path)
