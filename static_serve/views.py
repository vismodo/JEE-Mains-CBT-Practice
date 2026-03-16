from django.shortcuts import render
from django.http import FileResponse, HttpResponse
import os

def serve_static(request, path):
    # Validate the path to prevent directory traversal attacks
    base_dir = os.path.realpath('static/')
    file_path = os.path.realpath(os.path.join('static', path))
    
    # Ensure the requested file is within the static directory
    if not file_path.startswith(base_dir) or not os.path.isfile(file_path):
        return HttpResponse("File not found", status=404)
    
    try:
        return FileResponse(open(file_path, 'rb'))
    except (FileNotFoundError, IOError):
        return HttpResponse("File not found", status=404)

