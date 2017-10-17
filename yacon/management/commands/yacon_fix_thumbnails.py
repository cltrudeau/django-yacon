import os
from PIL import Image

from django.conf import settings
from django.core.management.base import BaseCommand

from yacon import conf

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not conf.site.auto_thumbnails:
            print('Auto thumbnails not configured, exiting')
            quit()

        thumb_dir = conf.site.auto_thumbnails['dir']
        thumb_conf = conf.site.auto_thumbnails['config']

        for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            print('processing dirpath: %s' % dirpath)
            if thumb_dir in dirpath:
                print('   skipping, thumb_dir in dirpath')
                continue

            for filename in filenames:
                print('   processing filename:', filename)
                extension = None
                if '.' in filename:
                    pieces = filename.split('.')
                    extension = pieces[-1]

                if extension not in conf.site.image_extensions:
                    print('      skipping, non image extension')
                    continue

                # if you get here then the file has an image extension
                full_filename = os.path.join(dirpath, filename)
                for thumb_type, size in thumb_conf.items():
                    image_dir = os.path.realpath(os.path.join(dirpath, 
                        thumb_dir, thumb_type))
                    image_name = os.path.join(image_dir, filename)
                    if os.path.exists(image_name):
                        print('      thumbnail already exists')
                        continue
                    try:
                        os.makedirs(image_dir)
                    except:
                        pass # already exists, do nothing

                    # use PIL to create the thumbnail
                    im = Image.open(full_filename)
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(image_name, 'png')
                    print('      created thumbnail:', image_name)
