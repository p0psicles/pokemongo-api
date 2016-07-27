import requests
from requests.compat import urljoin
import logging


def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('Line %(lineno)d,%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class PushBulletNotify(object):

    def __init__(self, pushbullet_api, pushbullet_device):
        self.session = requests.Session()
        self.url = 'https://api.pushbullet.com/v2/'
        self.pushbullet_api = pushbullet_api
        self.pushbullet_device = pushbullet_device

    def test_notify(self, pushbullet_api):
        logging.debug('Sending a test Pushbullet notification.')
        return self._send_pushbullet(
            pushbullet_api,
            event='Test',
            message='Testing Pushbullet settings from Medusa',
            force=True
        )

    def get_devices(self, pushbullet_api=None):
        logging.debug('Testing Pushbullet authentication and retrieving the device list.')
        headers = {'Access-Token': pushbullet_api or self.pushbullet_api}
        return self.session.get(urljoin(self.url, 'devices'), headers=headers).json() or {}

    def set_device(self, index=0):
        devices = self.get_devices()
        self.pushbullet_device = devices['devices'][index]['iden']

    def notify_pokemon(self, pokemon, poke_name=''):
        self._send_pushbullet(
            pushbullet_api=None,
            event='Found Pokemon',
            message='Found pokemon {0}'.format(poke_name if poke_name else '')
        )

    def _send_pushbullet(  # pylint: disable=too-many-arguments
            self, pushbullet_api=None, pushbullet_device=None, event=None, message=None, link=None, force=False):

        pushbullet_api = pushbullet_api or self.pushbullet_api
        pushbullet_device = pushbullet_device or self.pushbullet_device

        logging.debug('Pushbullet event: %r' % event)
        logging.debug('Pushbullet message: %r' % message)
        logging.debug('Pushbullet api: %r' % pushbullet_api)
        logging.debug('Pushbullet devices: %r' % pushbullet_device)

        post_data = {
            'title': event,
            'body': message,
            'device_iden': pushbullet_device,
            'type': 'link' if link else 'note'
        }
        if link:
            post_data['url'] = link

        headers = {'Access-Token': pushbullet_api}

        response = self.session.post(urljoin(self.url, 'pushes'), data=post_data, headers=headers).json() or {}
        if not response:
            return False

        failed = response.pop('error', {})
        if failed:
            logging.warning('Pushbullet notification failed: %s', failed.pop('message'))
        else:
            logging.debug('Pushbullet notification sent.')

        return False if failed else True
