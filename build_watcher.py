import sys
import os
import time
import subprocess
import logging
from argparse import ArgumentParser

try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except Exception:
    print('Missing watchdog. Install with: pip install watchdog')
    raise


LOG = logging.getLogger('build_watcher')


def run_build():
    script = os.path.join(os.path.dirname(__file__), 'build_exe.bat')
    if not os.path.exists(script):
        LOG.error('Build script not found: %s', script)
        return 1
    LOG.info('Running build script: %s', script)
    # Use shell to run the batch on Windows
    res = subprocess.run([script], shell=True)
    return res.returncode


class RebuildHandler(PatternMatchingEventHandler):
    def __init__(self, debounce=1.0):
        super().__init__(patterns=['*.py', '*.txt', '*.md'], ignore_directories=True)
        self._last = 0
        self.debounce = debounce

    def on_any_event(self, event):
        now = time.time()
        if now - self._last < self.debounce:
            return
        self._last = now
        LOG.info('Change detected: %s', event.src_path)
        rc = run_build()
        if rc != 0:
            LOG.error('Build failed with code %s', rc)
        else:
            LOG.info('Build completed successfully')


def main():
    parser = ArgumentParser(description='Watch project files and rebuild exe on change')
    parser.add_argument('--once', action='store_true', help='Run build once and exit')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

    if args.once:
        rc = run_build()
        sys.exit(rc)

    event_handler = RebuildHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    LOG.info('Watcher started. Watching for file changes...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
