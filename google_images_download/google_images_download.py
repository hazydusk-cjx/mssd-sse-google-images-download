"""
Searching and Downloading Google Images to the local disk
"""

import sys
import time
import os
import argparse
import ssl
import datetime
import json
import re
import codecs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
    import http.client
    from http.client import IncompleteRead, BadStatusLine

    http.client._MAXHEADERS = 1000
else:  # If the Current Version of Python is 2.x
    print("Python 2 not supported")


args_list = ["keywords", "keywords_from_file", "prefix_keywords",
             "suffix_keywords", "limit", "format", "color", "color_type",
             "usage_rights", "size", "exact_size", "aspect_ratio",
             "type", "time", "time_range", "delay", "url", "single_image",
             "output_directory", "image_directory", "no_directory", "proxy",
             "similar_images", "specific_site", "print_urls", "print_size",
             "print_paths", "metadata", "extract_metadata", "socket_timeout",
             "thumbnail", "thumbnail_only", "language", "prefix",
             "chromedriver", "related_images", "safe_search", "no_numbering",
             "offset", "no_download", "save_source", "silent_mode",
             "ignore_urls"]


def user_input():
    """parse in user input as argument"""
    config = argparse.ArgumentParser()
    config.add_argument('-cf', '--config_file', help='config file name',
                        default='', type=str, required=False)
    config_file_check = config.parse_known_args()
    object_check = vars(config_file_check[0])

    if object_check['config_file'] != '':
        records = []
#        json_file = json.load(open(config_file_check[0].config_file))
        with json.load(open(config_file_check[0].config_file)) as json_file:
            for record in range(0, len(json_file['Records'])):
                arguments = {}
                for i in args_list:
                    arguments[i] = None
                for key, value in json_file['Records'][record].items():
                    arguments[key] = value
                records.append(arguments)
#                records_count = len(records)
    else:
        # Taking command line arguments from users
        parser = argparse.ArgumentParser()

        parser.add_argument('-k', '--keywords', help='delimited list input',
                            type=str, required=False)

        parser.add_argument('-kf', '--keywords_from_file',
                            help='extract list of keywords from a text file',
                            type=str, required=False)

        parser.add_argument('-sk', '--suffix_keywords',
                            help=', separated additional words after keyword',
                            type=str, required=False)

        parser.add_argument('-pk', '--prefix_keywords',
                            help=', separated additional words before keyword',
                            type=str, required=False)

        parser.add_argument('-l', '--limit', help='delimited list input',
                            type=str, required=False)

        parser.add_argument('-f', '--format',
                            help='download images with specific format',
                            type=str, required=False,
                            choices=['jpg', 'gif', 'png',
                                     'bmp', 'svg', 'webp', 'ico'])

        parser.add_argument('-u', '--url',
                            help='search with google image URL',
                            type=str, required=False)

        parser.add_argument('-x', '--single_image',
                            help='downloading a single image from URL',
                            type=str, required=False)

        parser.add_argument('-o', '--output_directory',
                            help='download images in a ' +
                            'specific main directory',
                            type=str, required=False)

        parser.add_argument('-i', '--image_directory',
                            help='download images in a specific sub-directory',
                            type=str, required=False)

        parser.add_argument('-n', '--no_directory', default=False,
                            help='download images in main directory, ' +
                            ' but no sub-directory',
                            action="store_true")

        parser.add_argument('-d', '--delay',
                            help='delay(s) between downloading 2 images',
                            type=int, required=False)

        parser.add_argument('-co', '--color',
                            help='filter on color',
                            type=str, required=False,
                            choices=['red', 'orange', 'yellow', 'green',
                                     'teal', 'blue', 'purple', 'pink',
                                     'white', 'gray', 'black', 'brown'])

        parser.add_argument('-ct', '--color_type',
                            help='filter on color',
                            type=str, required=False,
                            choices=['full-color', 'black-and-white',
                                     'transparent'])

        parser.add_argument('-r', '--usage_rights',
                            help='usage rights', type=str, required=False,
                            choices=['labeled-for-reuse-with-modifications',
                                     'labeled-for-reuse',
                                     'labeled-for-noncommercial' +
                                     '-reuse-with-modification',
                                     'labeled-for-nocommercial-reuse'])

        parser.add_argument('-s', '--size',
                            help='image size',
                            type=str, required=False,
                            choices=['large', 'medium', 'icon',
                                     '>400*300', '>640*480', '>800*600',
                                     '>1024*768', '>2MP', '>4MP',
                                     '>6MP', '>8MP', '>10MP', '>12MP', '>15MP',
                                     '>20MP', '>40MP', '>70MP'])

        parser.add_argument('-es', '--exact_size',
                            help='exact image resolution "WIDTH,HEIGHT"',
                            type=str, required=False)

        parser.add_argument('-t', '--type',
                            help='image type',
                            type=str, required=False,
                            choices=['face', 'photo', 'clipart',
                                     'line-drawing', 'animated'])

        parser.add_argument('-w', '--time',
                            help='image age',
                            type=str, required=False,
                            choices=['past-24-hours', 'past-7-days',
                                     'past-month', 'past-year'])

        parser.add_argument('-wr', '--time_range',
                            help='time range for the age of the image. ' +
                            'should be in the format' +
                            '{"time_min":"YYYY-MM-DD",' +
                            '"time_max":"YYYY-MM-DD"}',
                            type=str, required=False)

        parser.add_argument('-a', '--aspect_ratio',
                            help='comma separated additional words ' +
                            ' added to keywords',
                            type=str,
                            required=False,
                            choices=['tall', 'square', 'wide', 'panoramic'])

        parser.add_argument('-si', '--similar_images',
                            help='downloads images very similar ' +
                            ' to the image URL you provide',
                            type=str, required=False)

        parser.add_argument('-ss', '--specific_site',
                            help='downloads images that are indexed ' +
                            ' from a specific website',
                            type=str, required=False)

        parser.add_argument('-p', '--print_urls', default=False,
                            help="Print the URLs of the images",
                            action="store_true")

        parser.add_argument('-ps', '--print_size', default=False,
                            help="Print the size of the images on disk",
                            action="store_true")

        parser.add_argument('-pp', '--print_paths', default=False,
                            help="Prints the list of absolute" +
                            "paths of the images",
                            action="store_true")

        parser.add_argument('-m', '--metadata', default=False,
                            help="Print the metadata of the image",
                            action="store_true")

        parser.add_argument('-e', '--extract_metadata', default=False,
                            help="Dumps all the logs into a text file",
                            action="store_true")

        parser.add_argument('-st', '--socket_timeout', default=False,
                            help="Connection timeout waiting " +
                            "for the image to download",
                            type=float)

        parser.add_argument('-th', '--thumbnail', default=False,
                            help="Downloads image thumbnail " +
                            "along with the actual image",
                            action="store_true")

        parser.add_argument('-tho', '--thumbnail_only', default=False,
                            help="Downloads only thumbnail without " +
                            "downloading actual images", action="store_true")
        parser.add_argument('-la', '--language', default=False,
                            help="Defines the language filter. " +
                            "The search results are authomatically " +
                            "returned in that language",
                            type=str, required=False,
                            choices=['Arabic', 'Chinese (Simplified)',
                                     'Chinese (Traditional)', 'Czech',
                                     'Danish', 'Dutch', 'English', 'Estonian',
                                     'Finnish', 'French', 'German', 'Greek',
                                     'Hebrew', 'Hungarian', 'Icelandic',
                                     'Italian', 'Japanese', 'Korean',
                                     'Latvian', 'Lithuanian', 'Norwegian',
                                     'Portuguese', 'Polish', 'Romanian',
                                     'Russian', 'Spanish', 'Swedish',
                                     'Turkish'])

        parser.add_argument('-pr', '--prefix', default=False,
                            help="A word that you would want to prefix " +
                            "in front of each image name", type=str,
                            required=False)

        parser.add_argument('-px', '--proxy',
                            help='specify a proxy address and port',
                            type=str, required=False)

        parser.add_argument('-cd', '--chromedriver',
                            help='specify the path to chromedriver ' +
                            'executable in your local machine',
                            type=str, required=False)

        parser.add_argument('-ri', '--related_images', default=False,
                            help="Downloads images that are similar " +
                            "to the keyword provided",
                            action="store_true")

        parser.add_argument('-sa', '--safe_search', default=False,
                            help="Turns on the safe search filter " +
                            "while searching for images",
                            action="store_true")

        parser.add_argument('-nn', '--no_numbering', default=False,
                            help="Allows you to exclude the default " +
                            "numbering of images", action="store_true")

        parser.add_argument('-of', '--offset',
                            help="Where to start in the fetched links",
                            type=str, required=False)

        parser.add_argument('-nd', '--no_download', default=False,
                            help="Prints the URLs of the images and/or " +
                            "thumbnails without downloading them",
                            action="store_true")
        parser.add_argument('-iu', '--ignore_urls', default=False,
                            help="delimited list input of image " +
                            "urls/keywords to ignore",
                            type=str)

        parser.add_argument('-sil', '--silent_mode', default=False,
                            help="Remains silent. Does not print " +
                            "notification messages on the terminal",
                            action="store_true")

        parser.add_argument('-is', '--save_source',
                            help="creates a text file containing " +
                            "a list of downloaded images along with " +
                            "source page url",
                            type=str, required=False)

        args = parser.parse_args()
        arguments = vars(args)
        records = []
        records.append(arguments)
    return records


class GoogleImagesDownload:
    '''google_images_download_class'''

    def __init__(self):
        pass

    def _extract_data_pack(self, page):
        start_line = page.find("AF_initDataCallback({key: \\'ds:1\\'") - 10
        start_object = page.find('[', start_line + 1)
        end_object = page.rfind(']', 0, page.find('</script>',
                                                  start_object + 1))+1
        object_raw = str(page[start_object:end_object])
        return bytes(object_raw, "utf-8").decode("unicode_escape")

    def _extract_data_pack_extended(self, page):
        start_line = page.find("AF_initDataCallback({key: 'ds:1'") - 10
        start_object = page.find('[', start_line + 1)
        end_object = page.rfind(']', 0, page.find('</script>',
                                                  start_object + 1)) + 1
        return str(page[start_object:end_object])

    def _extract_data_pack_ajax(self, data):
        lines = data.split('\n')
        return json.loads(lines[3])[0][2]

    def _image_objects_from_pack(self, data):
        image_objects = json.loads(data)[31][-1][12][2]
        image_objects = [x for x in image_objects if x[0] == 1]
        return image_objects

    def download_page(self, url):
        '''Downloading entire Web Document (Raw Page Content)'''
#        version = (3, 0)
#        cur_version = sys.version_info
        headers = {}
        headers['User-Agent'] = str("Mozilla/5.0 (Windows NT 10.0; " +
                                    "Win64; x64) AppleWebKit/537.36 " +
                                    "(KHTML, like Gecko) " +
                                    "Chrome/88.0.4324.104 Safari/537.36")

# If the Current Version of Python is 3.0 or above
        if cur_version >= version:
            try:
                req = urllib.request.Request(url, headers=headers)
#                resp = urllib.request.urlopen(req)
                with urllib.request.urlopen(req) as resp:
                    resp_data = str(resp.read())
            except Exception:
                print("Could not open URL. " +
                      "Please check your internet connection " +
                      "and/or ssl settings \n"
                      "If you are using proxy, make sure your " +
                      "proxy settings is configured correctly")
                sys.exit()
        else:  # If the Current Version of Python is 2.x
            print("Python 2 not supported")

        try:
            return (self._image_objects_from_pack(
                self._extract_data_pack(resp_data)),
                self.get_all_tabs(resp_data))
        except Exception as e_info:
            print(e_info)
            print('Image objects data unpacking failed. ' +
                  ' Please leave a comment with the above ' +
                  'error at https://github.com/hardikvasa/' +
                  'google-images-download/pull/298')
            sys.exit()

    # Download Page for more than 100 images
    def download_extended_page(self, url, chromedriver):
        '''Download Page for more than 100 images'''
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")

        try:
            browser = webdriver.Chrome(chromedriver, chrome_options=options)
        except Exception as e_info:
            print("Looks like we cannot locate the path the " +
                  " chromedriver' (use the '--chromedriver' "
                  "argument to specify the path to the executable.) " +
                  "or google chrome browser is not " +
                  "installed on your machine (exception: %s)" % e_info)
            sys.exit()
        browser.set_window_size(1024, 768)

        # Open the link
        browser.get(url)
        browser.execute_script("""
            (function(XHR){
                "use strict";
                var open = XHR.prototype.open;
                var send = XHR.prototype.send;
                var data = [];
                XHR.prototype.open = function(method, url, async, user, pass) {
                    this._url = url;
                    open.call(this, method, url, async, user, pass);
                }
                XHR.prototype.send = function(data) {
                    var self = this;
                    var url = this._url;
                    function stateChanged() {
                        if (self.readyState == 4) {
                            console.log("data available for: " + url)
                            XHR.prototype._data.push(self.response);
                        }
                    }
                    if (url.includes("/batchexecute?")) {
                        this.addEventListener("readystatechange",
                                              stateChanged, false);
                    }
                    send.call(this, data);
                };
                XHR.prototype._data = [];
            })(XMLHttpRequest);
        """)

        time.sleep(1)
        print("Getting you a lot of images. This may take a few moments...")

        element = browser.find_element_by_tag_name("body")
        # Scroll down
        for _ in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_xpath(
                '//input[@value="Show more results"]').click()
            for _ in range(50):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection
        except Exception:
            for _ in range(10):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)  # bot id protection

        print("Reached end of Page.")
        time.sleep(0.5)

        source = browser.page_source  # page source
        images = self._image_objects_from_pack(
            self._extract_data_pack_extended(source))

        ajax_data = browser.execute_script(
            "return XMLHttpRequest.prototype._data")
        for chunk in ajax_data:
            images += self._image_objects_from_pack(
                self._extract_data_pack_ajax(chunk))

        # close the browser
        browser.close()

        return images, self.get_all_tabs(source)

    # Finding 'Next Image' from the given raw page
    def get_next_tab(self, s_args):
        '''Finding 'Next Image' from the given raw page'''
        start_line = s_args.find('class="dtviD"')
        if start_line == -1:  # If no links are found then give an error!
            end_quote = 0
            link = "no_tabs"
            return link, '', end_quote
        else:
            start_line = s_args.find('class="dtviD"')
            start_content = s_args.find('href="', start_line + 1)
            end_content = s_args.find('">', start_content + 1)
            url_item = str("https://www.google.com" +
                           str(s_args[start_content + 6:end_content]))
            url_item = url_item.replace('&amp;', '&')

            start_line_2 = s_args.find('class="dtviD"')
            s_args = s_args.replace('&amp;', '&')
            start_content_2 = s_args.find(':', start_line_2 + 1)
            end_content_2 = s_args.find('&usg=', start_content_2 + 1)
            url_item_name = str(s_args[start_content_2 + 1:end_content_2])

            chars = url_item_name.find(',g_1:')
            chars_end = url_item_name.find(":", chars + 6)
            if chars_end == -1:
                updated_item_name = (
                    url_item_name[chars + 5:]).replace("+", " ")
            else:
                updated_item_name = (
                    url_item_name[chars + 5:chars_end]).replace("+", " ")

            return url_item, updated_item_name, end_content

    # Getting all links with the help of '_images_get_next_image'
    def get_all_tabs(self, page):
        '''Getting all links with the help of '_images_get_next_image' '''
        tabs = {}
        while True:
            item, item_name, end_content = self.get_next_tab(page)
            if item == "no_tabs":
                break
            else:
                if len(item_name) > 100 or item_name == "background-color":
                    break
                else:
                    # Append all the links in the list named 'Links'
                    tabs[item_name] = item
                    # Timer could be used to slow down
                    # the request for image downloads
                    time.sleep(0.1)
                    page = page[end_content:]
        return tabs

    # Format the object in readable format
    def format_object(self, object):
        '''Format the object in readable format'''
        data = object[1]
        main = data[3]
        info = data[9]
        if info is None:
            info = data[11]
        formatted_object = {}
        try:
            formatted_object['image_height'] = main[2]
            formatted_object['image_width'] = main[1]
            formatted_object['image_link'] = main[0]
            imgft = main[0][-1 * (len(main[0]) - main[0].rfind(".") - 1):]
            formatted_object['image_format'] = str(imgft)
            formatted_object['image_description'] = info['2003'][3]
            formatted_object['image_host'] = info['2003'][17]
            formatted_object['image_source'] = info['2003'][2]
            formatted_object['image_thumbnail_url'] = data[2][0]
        except Exception as e_info:
            print(e_info)
            return None
        return formatted_object

    # function to download single image
    def single_image(self, image_url):
        '''function to download single image'''
        main_directory = "downloads"
        extensions = (".jpg", ".gif", ".png", ".bmp", ".svg", ".webp", ".ico")
        url = image_url
        try:
            os.makedirs(main_directory)
        except OSError as e_info:
            if e_info.errno != 17:
                raise
#            pass
        req = Request(url,
                      headers={
                          "User-Agent":
                              "Mozilla/5.0 (X11; Linux i686) " +
                              "AppleWebKit/537.17 (KHTML, like " +
                              "Gecko) Chrome/24.0.1312.27 Safari/537.17"}
                      )

        with urlopen(req, None, 10) as response:
            data = response.read()
            response.close()

        image_name = str(url[(url.rfind('/')) + 1:])
        if '?' in image_name:
            image_name = image_name[:image_name.find('?')]
#       if ".jpg" in image_name or ".gif" in image_name or
#       ".png" in image_name or ".bmp" in image_name or
#       ".svg" in image_name or ".webp" in image_name or
#       ".ico" in image_name:
        if any(map(lambda extension: extension in image_name, extensions)):
            file_name = main_directory + "/" + image_name
        else:
            file_name = main_directory + "/" + image_name + ".jpg"
            image_name = image_name + ".jpg"

        try:
            with open(file_name, 'wb') as output_file:
                output_file.write(data)
                output_file.close()
        except IOError as e_info:
            raise e_info
#        except OSError as e_info:
#            raise e_info
        print("completed ====> " +
              image_name.encode('raw_unicode_escape').decode('utf-8'))
        return

    def similar_images(self, similar_images):
        '''download similar images'''
        try:
            search_url = (
                'https://www.google.com/searchbyimage?' +
                'site=search&sa=X&image_url=' + similar_images)
            headers = {}
            headers['User-Agent'] = ("Mozilla/5.0 (Windows NT 6.1) " +
                                     "AppleWebKit/537.36 (KHTML, " +
                                     "like Gecko) Chrome/41.0.2228.0 " +
                                     "Safari/537.36")

            req1 = urllib.request.Request(search_url, headers=headers)
#            resp1 = urllib.request.urlopen(req1)
            with urllib.request.urlopen(req1) as resp1:
                content = str(resp1.read())
                l_1 = content.find('AMhZZ')
                l_2 = content.find('&', l_1)
                urll = content[l_1:l_2]

                newurl = ("https://www.google.com/search?" +
                          "tbs=sbi:" + urll + "&site=search&sa=X")
                req2 = urllib.request.Request(newurl, headers=headers)
#               resp2 = urllib.request.urlopen(req2)
#               with urllib.request.urlopen(req2) as resp2:
                with urllib.request.urlopen(req2):
                    l_3 = content.find('/search?sa=X&amp;q=')
                    l_4 = content.find(';', l_3 + 19)
                    urll2 = content[l_3 + 19:l_4]
            return urll2
        except Exception:
            return "Cloud not connect to Google Images endpoint"

    # Building URL parameters
    def build_url_parameters(self, arguments):
        '''Building URL parameters'''
        if arguments['language']:
            lang = "&lr="
            lang_param = {"Arabic": "lang_ar",
                          "Chinese (Simplified)": "lang_zh-CN",
                          "Chinese (Traditional)": "lang_zh-TW",
                          "Czech": "lang_cs",
                          "Danish": "lang_da",
                          "Dutch": "lang_nl",
                          "English": "lang_en",
                          "Estonian": "lang_et",
                          "Finnish": "lang_fi",
                          "French": "lang_fr",
                          "German": "lang_de",
                          "Greek": "lang_el",
                          "Hebrew": "lang_iw ",
                          "Hungarian": "lang_hu",
                          "Icelandic": "lang_is",
                          "Italian": "lang_it",
                          "Japanese": "lang_ja",
                          "Korean": "lang_ko",
                          "Latvian": "lang_lv",
                          "Lithuanian": "lang_lt",
                          "Norwegian": "lang_no",
                          "Portuguese": "lang_pt",
                          "Polish": "lang_pl",
                          "Romanian": "lang_ro",
                          "Russian": "lang_ru",
                          "Spanish": "lang_es",
                          "Swedish": "lang_sv",
                          "Turkish": "lang_tr"}
            lang_url = lang + lang_param[arguments['language']]
        else:
            lang_url = ''

        built_url = "&tbs="
        counter = 0
        params = {'color': [arguments['color'],
                            {'red': 'ic:specific,isc:red',
                             'orange': 'ic:specific,isc:orange',
                             'yellow': 'ic:specific,isc:yellow',
                             'green': 'ic:specific,isc:green',
                             'teal': 'ic:specific,isc:teel',
                             'blue': 'ic:specific,isc:blue',
                             'purple': 'ic:specific,isc:purple',
                             'pink': 'ic:specific,isc:pink',
                             'white': 'ic:specific,isc:white',
                             'gray': 'ic:specific,isc:gray',
                             'black': 'ic:specific,isc:black',
                             'brown': 'ic:specific,isc:brown'}],
                  'color_type': [arguments['color_type'],
                                 {'full-color': 'ic:color',
                                  'black-and-white': 'ic:gray',
                                  'transparent': 'ic:trans'}],
                  'usage_rights': [arguments['usage_rights'],
                                   {'labeled-for-reuse-with' +
                                    '-modifications': 'sur:fmc',
                                    'labeled-for-reuse': 'sur:fc',
                                    'labeled-for-noncommercial-' +
                                    'reuse-with-modification': 'sur:fm',
                                    'labeled-for-nocommercial-reuse': 'sur:f'}
                                   ],
                  'size': [arguments['size'],
                           {'large': 'isz:l', 'medium': 'isz:m',
                            'icon': 'isz:i', '>400*300': 'isz:lt,islt:qsvga',
                            '>640*480': 'isz:lt,islt:vga',
                            '>800*600': 'isz:lt,islt:svga',
                            '>1024*768': 'visz:lt,islt:xga',
                            '>2MP': 'isz:lt,islt:2mp',
                            '>4MP': 'isz:lt,islt:4mp',
                            '>6MP': 'isz:lt,islt:6mp',
                            '>8MP': 'isz:lt,islt:8mp',
                            '>10MP': 'isz:lt,islt:10mp',
                            '>12MP': 'isz:lt,islt:12mp',
                            '>15MP': 'isz:lt,islt:15mp',
                            '>20MP': 'isz:lt,islt:20mp',
                            '>40MP': 'isz:lt,islt:40mp',
                            '>70MP': 'isz:lt,islt:70mp'}],
                  'type': [arguments['type'], {'face': 'itp:face',
                                               'photo': 'itp:photo',
                                               'clipart': 'itp:clipart',
                                               'line-drawing': 'itp:lineart',
                                               'animated': 'itp:animated'}],
                  'time': [arguments['time'], {'past-24-hours': 'qdr:d',
                                               'past-7-days': 'qdr:w',
                                               'past-month': 'qdr:m',
                                               'past-year': 'qdr:y'}],
                  'aspect_ratio': [arguments['aspect_ratio'],
                                   {'tall': 'iar:t',
                                    'square': 'iar:s',
                                    'wide': 'iar:w',
                                    'panoramic': 'iar:xw'}],
                  'format': [arguments['format'],
                             {'jpg': 'ift:jpg',
                              'gif': 'ift:gif',
                              'png': 'ift:png',
                              'bmp': 'ift:bmp',
                              'svg': 'ift:svg',
                              'webp': 'webp',
                              'ico': 'ift:ico',
                              'raw': 'ift:craw'}]}
        for _, value in params.items():
            if value[0] is not None:
                ext_param = value[1][value[0]]
                # counter will tell if it is first param added or not
                if counter == 0:
                    # add it to the built url
                    built_url = built_url + ext_param
                    counter += 1
                else:
                    built_url = built_url + ',' + ext_param
                    counter += 1
        built_url = lang_url + built_url
        return built_url

    # building main search URL
    def build_search_url(self, search_term, params, url,
                         similar_images, specific_site, safe_search):
        '''building main search URL'''
        # check safe_search
        safe_search_string = "&safe=active"
        # check the args and choose the URL
        if url:
            url = url

        elif similar_images:
            print(similar_images)
            keywordem = self.similar_images(similar_images)
            url = str('https://www.google.com/search?q=' +
                      keywordem +
                      '&espv=2&biw=1366&bih=667&site=webhp&' +
                      'source=lnms&tbm=isch&sa=X&ei=XosDVaCX' +
                      'D8TasATItgE&ved=0CAcQ_AUoAg')
        elif specific_site:
            url = ('https://www.google.com/search?q=' +
                   quote(search_term.encode('utf-8')) +
                   '&as_sitesearch=' +
                   specific_site +
                   '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch'
                   + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg')
        else:
            url = ('https://www.google.com/search?q=' +
                   quote(search_term.encode('utf-8')) +
                   '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' +
                   params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg')

        # safe search check
        if safe_search:
            url = url + safe_search_string

        return url

    # measures the file size
    def file_size(self, file_path):
        '''measures the file size'''
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            size = file_info.st_size
            for x_var in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return "%3.1f %s" % (size, x_var)
                size /= 1024.0
            return size

    # keywords from file
    def keywords_from_file(self, file_name):
        '''keywords from file'''
        search_keyword = []
        with codecs.open(file_name, 'r', encoding='utf-8-sig') as f_file:
            if '.csv' in file_name:
                for line in f_file:
                    if line in ['\n', '\r\n']:
                        pass
                    else:
                        search_keyword.append(
                            line.replace('\n', '').replace('\r', ''))
            elif '.txt' in file_name:
                for line in f_file:
                    if line in ['\n', '\r\n']:
                        pass
                    else:
                        search_keyword.append(
                            line.replace('\n', '').replace('\r', ''))
            else:
                print("Invalid file type: Valid file " +
                      "types are either .txt or .csv \n"
                      "exiting...")
                sys.exit()
        return search_keyword

    # make directories
    def create_directories(self, main_directory,
                           dir_name, thumbnail, thumbnail_only):
        '''make directories'''
        dir_name_thumbnail = dir_name + " - thumbnail"
        # make a search keyword  directory
        try:
            if not os.path.exists(main_directory):
                os.makedirs(main_directory)
                time.sleep(0.15)
                path = (dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
                if thumbnail or thumbnail_only:
                    sub_directory_thumbnail = os.path.join(
                        main_directory, dir_name_thumbnail)
                    if not os.path.exists(sub_directory_thumbnail):
                        os.makedirs(sub_directory_thumbnail)
            else:
                path = (dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
                if thumbnail or thumbnail_only:
                    sub_directory_thumbnail = os.path.join(
                        main_directory, dir_name_thumbnail)
                    if not os.path.exists(sub_directory_thumbnail):
                        os.makedirs(sub_directory_thumbnail)
        except OSError as e_info:
            if e_info.errno != 17:
                raise
#            pass
        return

    # Download Image thumbnails
    def download_image_thumbnail(self, image_url, main_directory, dir_name,
                                 return_image_name, print_urls,
                                 socket_timeout, print_size, no_download,
                                 save_source, img_src, ignore_urls):
        '''Download Image thumbnails'''
        if print_urls or no_download:
            print("Image URL: " + image_url)
        if no_download:
            return "success", "Printed url without downloading"
        try:
            req = Request(image_url,
                          headers={"User-Agent":
                                   "Mozilla/5.0 (X11; Linux i686) " +
                                   "AppleWebKit/537.17 (KHTML, like " +
                                   "Gecko) Chrome/24.0.1312.27 Safari/537.17"})
            try:
                # timeout time to download an image
                if socket_timeout:
                    timeout = float(socket_timeout)
                else:
                    timeout = 10

#                response = urlopen(req, None, timeout)
                with urlopen(req, None, timeout) as response:
                    data = response.read()
#                response.close()

                path = (main_directory + "/" + dir_name +
                        " - thumbnail" + "/" + return_image_name)
#                   output_file = open(path, 'wb')
                try:
                    with open(path, 'wb') as output_file:
                        output_file.write(data)
                        output_file.close()
                        if save_source:
                            list_path = (main_directory + "/" +
                                         save_source + ".txt")
#                            list_file = open(list_path, 'a')
                            with open(list_path, 'a') as list_file:
                                list_file.write(path + '\t' + img_src + '\n')
#                               list_file.close()
                except OSError as e_info:
                    download_status = 'fail'
                    download_message = ("OSError on an image..." +
                                        "trying next one..." +
                                        " Error: " + str(e_info))
#                except IOError as e_info:
#                    download_status = 'fail'
#                    download_message = ("IOError on an image..." +
#                                        "trying next one..." +
#                                        " Error: " + str(e_info))

                download_status = 'success'
                download_message = ("Completed Image Thumbnail ====> " +
                                    return_image_name)

                # image size parameter
                if print_size:
                    print("Image Size: " + str(self.file_size(path)))

            except UnicodeEncodeError as e_info:
                download_status = 'fail'
                download_message = ("UnicodeEncodeError on an image..." +
                                    "trying next one..." +
                                    " Error: " + str(e_info))

        except HTTPError as e_info:  # If there is any HTTPError
            download_status = 'fail'
            download_message = ("HTTPError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))

        except URLError as e_info:
            download_status = 'fail'
            download_message = ("URLError on an image.." +
                                ".trying next one..." +
                                " Error: " + str(e_info))

        except ssl.CertificateError as e_info:
            download_status = 'fail'
            download_message = ("CertificateError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))

        except IOError as e_info:  # If there is any IOError
            download_status = 'fail'
            download_message = ("IOError on an image..."
                                + "trying next one..." +
                                " Error: " + str(e_info))
        return download_status, download_message

    # Download Images
    def download_image(self, image_url, image_format, main_directory,
                       dir_name, count, print_urls, socket_timeout,
                       prefix, print_size, no_numbering, no_download,
                       save_source, img_src, silent_mode, thumbnail_only,
                       format, ignore_urls):
        '''Download Images'''
        regex = re.compile('[^a-zA-Z0-9]')
        if not silent_mode:
            if print_urls or no_download:
                print("Image URL: " + image_url)
        if ignore_urls:
            if any(url in image_url for url in ignore_urls.split(',')):
                return ("fail",
                        "Image ignored due to 'ignore url' parameter",
                        None, image_url)
        if thumbnail_only:
            return ("success",
                    "Skipping image download...",
                    str(image_url[(image_url.rfind('/')) + 1:]),
                    image_url)
        if no_download:
            return ("success",
                    "Printed url without downloading",
                    None, image_url)
        try:
            req = Request(image_url,
                          headers={"User-Agent":
                                   "Mozilla/5.0 (X11; Linux i686)" +
                                   " AppleWebKit/537.17 (KHTML, like" +
                                   " Gecko) Chrome/24.0.1312.27 " +
                                   "Safari/537.17"})
            try:
                # timeout time to download an image
                if socket_timeout:
                    timeout = float(socket_timeout)
                else:
                    timeout = 10

#                response = urlopen(req, None, timeout)
                with urlopen(req, None, timeout) as response:
                    data = response.read()
                    info = response.info()
#                response.close()

                qmark = image_url.rfind('?')
                if qmark == -1:
                    qmark = len(image_url)
                slash = image_url.rfind('/', 0, qmark) + 1
                image_name = str(image_url[slash:qmark]).lower()

                type = info.get_content_type()
                
                # compare picture pull from url with user request 
                if req_file_format in type:

                    if type == "image/jpeg" or type == "image/jpg":
                        if (not image_name.endswith(
                                ".jpg") and not image_name.endswith(".jpeg")):
                            image_name += ".jpg"
                    elif type == "image/png":
                        if not image_name.endswith(".png"):
                            image_name += ".png"
                    elif type == "image/webp":
                        if not image_name.endswith(".webp"):
                            image_name += ".webp"
                    elif type == "image/gif":
                        if not image_name.endswith(".gif"):
                            image_name += ".gif"
                    elif type == "image/bmp" or type == "image/x-windows-bmp":
                        if not image_name.endswith(".bmp"):
                            image_name += ".bmp"
                    elif type == "image/x-icon":
                        if not image_name.endswith(".ico"):
                            image_name += ".ico"
                    elif type == "image/vnd.microsoft.icon":
                        if not image_name.endswith(".ico"):
                            image_name += ".ico"
                    elif type == "image/svg+xml":
                        if not image_name.endswith(".svg"):
                            image_name += ".svg"
                    else:
                        download_status = 'fail'
                        download_message = ("Invalid image format '" +
                                            type + "'. Skipping...")
                        return_image_name = ''
                        absolute_path = ''
                        return (download_status, download_message,
                                return_image_name, absolute_path)

                    # prefix name in image
                    if prefix:
                        prefix = str(regex.sub('', prefix)) + "-"
                    else:
                        prefix = ''

                    if no_numbering:
                        path = (main_directory + "/" +
                                dir_name + "/" + prefix + image_name)
                    else:
                        path = (main_directory + "/" +
                                dir_name + "/" + prefix + str(count)
                                + "." + image_name)

                    try:
                        with open(path, 'wb') as output_file:
                            output_file.write(data)
    #                    output_file = open(path, 'wb')
    #                    output_file.close()
                        if save_source:
                            list_path = main_directory + "/" + save_source + ".txt"
    #                        list_file = open(list_path, 'a')
                            with open(list_path, 'a') as list_file:
                                list_file.write(path + '\t' + img_src + '\n')
    #                        list_file.close()
                        absolute_path = os.path.abspath(path)
                    except OSError as e_info:
                        download_status = 'fail'
                        download_message = ("OSError on an image..." +
                                            "trying next one..." +
                                            " Error: " + str(e_info))
                        return_image_name = ''
                        absolute_path = ''

    # return image name back to calling method to use it for thumbnail downloads
                    download_status = 'success'
                    download_message = ("Completed Image ====> " +
                                        prefix + str(count) + "." + image_name)
                    return_image_name = prefix + str(count) + "." + image_name

    # image size parameter
                    if not silent_mode:
                        if print_size:
                            print("Image Size: " + str(self.file_size(path)))

                # return status as fail when file format does not matched
                else:
                    download_status = 'fail'
                    download_message = "File format not matched with user input...trying next one..."    
                    return_image_name = ''
                    absolute_path = ''
                        
            except UnicodeEncodeError as e_info:
                download_status = 'fail'
                download_message = ("UnicodeEncodeError on an image..." +
                                    "trying next one..." +
                                    " Error: " + str(e_info))
                return_image_name = ''
                absolute_path = ''

            except URLError as e_info:
                download_status = 'fail'
                download_message = ("URLError on an image..." +
                                    "trying next one..." +
                                    " Error: " + str(e_info))
                return_image_name = ''
                absolute_path = ''

            except BadStatusLine as e_info:
                download_status = 'fail'
                download_message = ("BadStatusLine on an image..." +
                                    "trying next one..." +
                                    " Error: " + str(e_info))
                return_image_name = ''
                absolute_path = ''

        except HTTPError as e_info:  # If there is any HTTPError
            download_status = 'fail'
            download_message = ("HTTPError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))
            return_image_name = ''
            absolute_path = ''

        except URLError as e_info:
            download_status = 'fail'
            download_message = ("URLError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))
            return_image_name = ''
            absolute_path = ''

        except ssl.CertificateError as e_info:
            download_status = 'fail'
            download_message = ("CertificateError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))
            return_image_name = ''
            absolute_path = ''

        except IOError as e_info:  # If there is any IOError
            download_status = 'fail'
            download_message = ("IOError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))
            return_image_name = ''
            absolute_path = ''

        except IncompleteRead as e_info:
            download_status = 'fail'
            download_message = ("IncompleteReadError on an image..." +
                                "trying next one..." +
                                " Error: " + str(e_info))
            return_image_name = ''
            absolute_path = ''

        return (download_status, download_message,
                return_image_name, absolute_path)

    def _get_all_items(self, image_objects, main_directory,
                       dir_name, limit, arguments):
        '''get all the items'''
        regex = re.compile('[^a-zA-Z0-9]')
        regexint = re.compile('[^0-9]')
        items = []
        abs_path = []
        error_count = 0
        i = 0
        count = 1
        while count < limit + 1 and i < len(image_objects):
            if len(image_objects) == 0:
                print("no_links")
                break
# code added here to attempt to implement offset correctly
# was "count < int(arguments['offset'])" in hardikvasa code, this seems
# to be contrary to the implementation details.
            elif arguments['offset'] and count <= int(regexint.sub('', str(
                    arguments['offset']))):
                count += 1
# page = page[end_content:]
            else:
                # format the item for readability
                object = self.format_object(image_objects[i])
                if arguments['metadata']:
                    if not arguments["silent_mode"]:
                        print("\nImage Metadata: " + str(object))

                # download the images
                d_s, d_m, r_in, a_p = self.download_image(
                    object['image_link'],
                    object['image_format'],
                    main_directory,
                    dir_name,
                    count,
                    arguments['print_urls'],
                    arguments['socket_timeout'],
                    arguments['prefix'],
                    arguments['print_size'],
                    arguments['no_numbering'],
                    arguments['no_download'],
                    arguments['save_source'],
                    object['image_source'],
                    arguments["silent_mode"],
                    arguments["thumbnail_only"],
                    arguments['format'],
                    arguments['ignore_urls'])
                download_status = d_s
                download_message = d_m
                return_image_name = r_in
                absolute_path = a_p
                if not arguments["silent_mode"]:
                    print(download_message)
                if download_status == "success":

                    # download image_thumbnails
                    if arguments['thumbnail'] or arguments["thumbnail_only"]:
                        d_s, d_mt = self.download_image_thumbnail(
                            object['image_thumbnail_url'],
                            main_directory,
                            dir_name,
                            return_image_name,
                            arguments['print_urls'],
                            arguments['socket_timeout'],
                            arguments['print_size'],
                            arguments['no_download'],
                            arguments['save_source'],
                            object['image_source'],
                            arguments['ignore_urls'])
                        download_status = d_s
                        download_message_thumbnail = d_mt
                        if not arguments["silent_mode"]:
                            print(download_message_thumbnail)

                    count += 1
                    object['image_filename'] = return_image_name
# Append all the links in the list named 'Links'
                    items.append(object)
                    abs_path.append(absolute_path)
                else:
                    error_count += 1

                # delay param
                if arguments['delay']:
                    time.sleep(int(arguments['delay']))
            i += 1
        if count < limit:
            print("\n\nUnfortunately all " + str(
                limit) +
                " could not be downloaded because some" +
                " images were not downloadable. " + str(
                count - 1) + " is all we got for this search filter!")
        return items, error_count, abs_path

    # Bulk Download
    def download(self, arguments):
        '''Bulk Download'''
        paths_agg = {}
        # for input coming from other python files
        if __name__ != "__main__":
            # if the calling file contains config_file param
            if 'config_file' in arguments:
                records = []
#                json_file = json.load(open(arguments['config_file']))
                with json.load(open(arguments['config_file'])) as json_file:
                    for record in range(0, len(json_file['Records'])):
                        arguments = {}
                        for i in args_list:
                            arguments[i] = None
                        for key, value in json_file['Records'][record].items():
                            arguments[key] = value
                        records.append(arguments)
                    total_errors = 0
                    for rec in records:
                        paths, errors = self.download_executor(rec)
                        for i in paths.items():
                            paths_agg[i] = paths[i]
                        if not arguments["silent_mode"]:
                            if arguments['print_paths']:
                                if isinstance(paths, str):
                                    print(paths)
                        total_errors = total_errors + errors
                return paths_agg, total_errors
            # if the calling file contains params directly
            else:
                paths, errors = self.download_executor(arguments)
                for i in paths.items():
                    paths_agg[i] = paths[i]
                if not arguments["silent_mode"]:
                    if arguments['print_paths']:
                        if isinstance(paths, str):
                            print(paths)
                return paths_agg, errors
        # for input coming from CLI
        else:
            paths, errors = self.download_executor(arguments)
            for i in paths.items():
                paths_agg[i] = paths[i]
            if not arguments["silent_mode"]:
                if arguments['print_paths']:
                    if isinstance(paths, str):
                        print(paths)
        return paths_agg, errors

    def download_executor(self, arguments):
        '''download executor function'''
        paths = {}
        regex = re.compile('[^a-zA-Z0-9]')
        error_count = None
        for arg in args_list:
            if arg not in arguments:
                arguments[arg] = None
# Initialization and Validation of user arguments
        if arguments['keywords']:
            search_keyword = [
                str(regex.sub('', item)) for item in arguments[
                    'keywords'].split(',')]

        if arguments['keywords_from_file']:
            search_keyword = self.keywords_from_file(
                arguments['keywords_from_file'])

# both time and time range should not be allowed in the same query
        if arguments['time'] and arguments['time_range']:
            raise ValueError(
                'Either time or time range should be used in a query.' +
                ' Both cannot be used at the same time.')

# both time and time range should not be allowed in the same query
        if arguments['size'] and arguments['exact_size']:
            raise ValueError(
                'Either "size" or "exact_size" should be used in a query.' +
                ' Both cannot be used at the same time.')

# both image directory and no image directory
# should not be allowed in the same query
        if arguments['image_directory'] and arguments['no_directory']:
            raise ValueError('You can either specify image directory ' +
                             'or specify no image directory, not both!')

# Additional words added to keywords
        if arguments['suffix_keywords']:
            suffix_keywords = [
                " " + str(sk)
                for sk in arguments['suffix_keywords'].split(',')]
        else:
            suffix_keywords = ['']

# Additional words added to keywords
        if arguments['prefix_keywords']:
            prefix_keywords = [
                str(regex.sub('', sk)) + " "
                for sk in arguments['prefix_keywords'].split(',')]
        else:
            prefix_keywords = ['']

# Setting limit on number of images to be downloaded
        if arguments['limit']:
            limit = int(arguments['limit'])
        else:
            limit = 100

        if arguments['url']:
            current_time = str(
                datetime.datetime.now()).split('.', maxsplit=1)[0]
            search_keyword = [current_time.replace(":", "_")]

        if arguments['similar_images']:
            current_time = str(
                datetime.datetime.now()).split('.', maxsplit=1)[0]
            search_keyword = [current_time.replace(":", "_")]

# If single_image or url argument not present
# then keywords is mandatory argument
        if arguments[
                'single_image'] is None and arguments[
                'url'] is None and arguments[
                    'similar_images'] is None and \
                arguments[
                    'keywords'] is None and arguments[
                    'keywords_from_file'] is None:
            print('-------------------------------\n'
                  'Uh oh! Keywords is a required argument \n\n'
                  'Please refer to the documentation ' +
                  'on guide to writing queries \n'
                  'https://github.com/hardikvasa/' +
                  'google-images-download#examples'
                  '\n\nexiting!\n'
                  '-------------------------------')
            sys.exit()

        # If this argument is present, set the custom output directory
        if arguments['output_directory']:
            main_directory = str(regex.sub('', arguments['output_directory']))
        else:
            main_directory = "downloads"

        # Proxy settings
        if arguments['proxy']:
            os.environ["http_proxy"] = arguments['proxy']
            os.environ["https_proxy"] = arguments['proxy']

        # Add time range to keywords if asked
        time_range = ''
        if arguments['time_range']:
            json_acceptable_string = arguments['time_range'].replace("'", "\"")
            d_info = json.loads(json_acceptable_string)
            time_range = (
                ' after:' + d_info['time_min'] +
                ' before:' + d_info['time_max'])

        exact_size = ''
        if arguments['exact_size']:
            size_array = [x.strip()
                          for x in arguments['exact_size'].split(',')]
            exact_size = (" imagesize:" +
                          str(size_array[0]) + "x" + str(size_array[1]))

# Initialization Complete
        total_errors = 0
        for pky in prefix_keywords:  # 1.for every prefix keywords
            for sky in suffix_keywords:  # 2.for every suffix keywords
                i = 0
                while i < len(search_keyword):  # 3.for every main keyword
                    iteration = ("\n" + "Item no.: " +
                                 str(i + 1) + " -->" +
                                 " Item name = " + (pky) +
                                 (search_keyword[i]) + (sky))
                    if not arguments["silent_mode"]:
                        print(iteration.encode(
                            'raw_unicode_escape').decode('utf-8'))
                        print("Evaluating...")
                    else:
                        print("Downloading images for: " +
                              (pky) + (search_keyword[i]) + (sky) + " ...")
                    search_term = pky + search_keyword[i] + sky

                    if arguments['image_directory']:
                        dir_name = str(regex.sub('',
                                                 arguments['image_directory']))
                    elif arguments['no_directory']:
                        dir_name = ''
# sub-directory
                    else:
                        dir_name = (search_term +
                                    ('-' +
                                     arguments['color']
                                     if arguments['color'] else ''))
# create directories in OS
                    if not arguments["no_download"]:
                        self.create_directories(main_directory, dir_name,
                                                arguments['thumbnail'],
                                                arguments['thumbnail_only'
                                                          ])

                    params = self.build_url_parameters(
                        arguments)  # building URL with params

                    search_term += time_range + exact_size
# building main search url
                    url = self.build_search_url(search_term, params,
                                                arguments['url'],
                                                arguments['similar_images'],
                                                arguments['specific_site'],
                                                arguments['safe_search'])

                    if limit < 101:
                        images, tabs = self.download_page(url)  # download page
                    else:
                        images, tabs = self.download_extended_page(
                            url, arguments['chromedriver'])

                    if not arguments["silent_mode"]:
                        if arguments['no_download']:
                            print("Getting URLs without downloading images...")
                        else:
                            print("Starting Download...")
# get all image items and download images
                    items, error_count, abs_path = self._get_all_items(
                        images,
                        main_directory,
                        dir_name,
                        limit,
                        arguments)
#                    paths[str(pky + search_keyword[i] + sky)] = abs_path

                    # dumps into a json file
                    if arguments['extract_metadata']:
                        try:
                            if not os.path.exists("logs"):
                                os.makedirs("logs")
                        except OSError as e_info:
                            print(e_info)
#                        json_file = open("logs/" + search_keyword[i] +
#                                         ".json", "w")
                        with open(
                                "logs/" + search_keyword[i] +
                                ".json", "w") as json_file:
                            json.dump(
                                items, json_file, indent=4, sort_keys=True)
                            json_file.close()

                    # Related images
                    if arguments['related_images']:
                        print("\nGetting list of related keywords..." +
                              "this may take a few moments")
                        for key, value in tabs.items():
                            final_search_term = (search_term + " - " + key)
                            print("\nNow Downloading - " + final_search_term)
# download page
                            if limit < 101:
                                images, _ = self.download_page(value)
                            else:
                                images, _ = self.download_extended_page(
                                    value, arguments['chromedriver'])
                            self.create_directories(main_directory,
                                                    final_search_term,
                                                    arguments['thumbnail'],
                                                    arguments['thumbnail' +
                                                              '_only'])
                            self._get_all_items(images,
                                                main_directory,
                                                search_term + " - " +
                                                key, limit, arguments)

                    i += 1
                    total_errors = total_errors + error_count
                    if not arguments["silent_mode"]:
                        print("\nErrors: " + str(error_count) + "\n")
        return paths, total_errors


# ------------- Main Program -------------#
def main():
    '''main program'''
    records = user_input()
    total_errors = 0
    t_0 = time.time()  # start the timer
    global req_file_format 
    req_file_format = records[0]['format']
    for arguments in records:

        # Download Single Image using a URL
        if arguments['single_image']:
            response = GoogleImagesDownload()
            response.single_image(arguments['single_image'])
# or download multiple images based on keywords/keyphrase search
        else:
            response = GoogleImagesDownload()

# wrapping response in a variable just for consistency
            paths, errors = response.download(arguments)
            total_errors = total_errors + errors

# stop the timer
        t_1 = time.time()
# Calculating the total time required to crawl
# to find and download all the links of 60,000 images
        total_time = t_1 - t_0
        if not arguments["silent_mode"]:
            print("\nEverything downloaded!")
            print("Total errors: " + str(total_errors))
            print("Total time taken: " + str(total_time) + " Seconds")


if __name__ == "__main__":
    main()
