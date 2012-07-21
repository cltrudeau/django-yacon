# yacon.views.uploads.py

import logging

from django.core.files.uploadedfile import UploadedFile
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon.decorators import superuser_required
from yacon.models import StoredFile
from yacon.utils import JSONResponse

logger = logging.getLogger(__name__)

# ============================================================================
# Helpers
# ============================================================================

def _file_hash(file_obj):
    data = {
        'name':'%s' % file_obj.file_field,
        'size':file_obj.file_field.file.size,
        'url':file_obj.file_field.url,
        #'thumbnail_url':file_obj.file_field.url,
    }

    return data

# ============================================================================
# Upload Management Tab
# ============================================================================

#@superuser_required
def uploads_tab(request):
    return render_to_response('nexus/uploads/uploader.html', {}, 
        context_instance=RequestContext(request))


#@superuser_required
def uploads_tab2(request):
    return render_to_response('nexus/uploads/z.html', {}, 
        context_instance=RequestContext(request))


#@superuser_required
@csrf_exempt
def upload_file(request):
    if request.method == 'GET':
        # return a list of the current files
        results = []
        for file_obj in StoredFile.objects.all():
            results.append(_file_hash(file_obj))

        return JSONResponse(results)

    # else: request == POST
    #import pudb; pudb.set_trace()
    if not request.FILES:
        error = 'request without files attached'
        logger.error(error)
        return HttpResponseBadRequest(error)

    # save the uploaded file
    field = request.FILES['files[]']
    wrapped_file = UploadedFile(field)
    stored = StoredFile.objects.create(file_field=field)

    results = [_file_hash(stored)]

    # IE has problems with JSON wrt the plug-in we're using, hack the mimetype
    # to get around the issue
    if 'application/json' not in request.META['HTTP_ACCEPT_ENCODING']:
        return JSONResponse(results, mimetype='text/plain')

    return JSONResponse(results)
