from google.cloud import translate

# See https://github.com/GoogleCloudPlatform/python-docs-samples
# /blob/master/translate/cloud-client/snippets.py for more reference.

class TranslateResult(object):
    """Contains translated texts."""
    def __init__(self, result):
        self.translated_text=result['translatedText']

def translate_text(target, text):
    # [START translate_translate_text]
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    use https://cloud.google.com/translate/docs/languages 
    to get the supported languages.
    """
    translate_client = translate.Client()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    # format_='text' is to change the html encoding to text.
    result = translate_client.translate(text, target_language=target, format_='text')
    
    return TranslateResult(result)

