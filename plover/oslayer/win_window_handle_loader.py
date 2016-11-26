import sys
import io
try:
    import simplejson as json
except ImportError:
    import json

def load_window_handles(filename):
	for encoding in ('utf-8', 'latin-1'):
		try:
			with io.open(filename, 'r', encoding=encoding) as fp:
				window_handles = json.load(fp)
				break
		except UnicodeDecodeError:
			continue
	else:
		raise ValueError('\'%s\' encoding could not be determined' % (filename,))

	return window_handles


def save_window_handles(filename, handles):
    with io.open(filename, 'w', encoding='utf-8') as fp:
        window_handles = json.dumps(handles)
        fp.write(unicode(window_handles, 'utf-8'))
