# yacon.views.uploads.py

import os, logging, json
from io import FileIO, BufferedWriter

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from yacon.decorators import superuser_required
from yacon.models import StoredFile

logger = logging.getLogger(__name__)

# ============================================================================

BUFFER_SIZE = 10485760  # 10MB

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
        print 'using iframe'
        #import pudb; pudb.set_trace()
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
