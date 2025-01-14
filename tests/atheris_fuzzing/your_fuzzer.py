import atheris
import re
from google_images_download import GoogleImagesDownload

with atheris.instrument_imports():
    import sys
    import warnings

# Suppress all warnings.
#warnings.simplefilter("ignore")

response = GoogleImagesDownload()

@atheris.instrument_func
def TestOneInput(input_bytes):
    regex = re.compile('[^a-zA-Z0-9]')

    fdp1 = atheris.FuzzedDataProvider(input_bytes[0:8])
    data1 = regex.sub('', fdp1.ConsumeUnicode(sys.maxsize))
#    data1 = fdp1.ConsumeUnicode(sys.maxsize)

    fdp2 = atheris.FuzzedDataProvider(input_bytes[8:16])
    data2 = fdp2.ConsumeUnicode(sys.maxsize)

    fdp3 = atheris.FuzzedDataProvider(input_bytes[16:24])
    data3 = fdp3.ConsumeUnicode(sys.maxsize)

    fdp4 = atheris.FuzzedDataProvider(input_bytes[24:32])
    data4 = fdp4.ConsumeUnicode(sys.maxsize)

    fdp5 = atheris.FuzzedDataProvider(input_bytes[32:34])
    data5 = fdp5.ConsumeIntInRange(1,5)

    fdp6 = atheris.FuzzedDataProvider(input_bytes[32:34])
    data6 = fdp6.ConsumeBool()

    if( (len(data1) == 0) ):
        return

    arguments = {
        "keywords": data1,
        "prefix_keywords": data2,
        "suffix_keywords": data3, 
        "image_directory": data4, 
        "limit": data5,
        "print_urls": data6
        }
    
    #print('X', ':'.join(hex(ord(x))[2:] for x in input_bytes))
    #printData(argumnets)
    #print(argumnets)
       
    try:
        iterator = response.download(arguments)
        for _ in iterator:
            pass
        
    except Exception:
        input_type = str(type(data1))
        codepoints = [hex(ord(x)) for x in data1]
        sys.stderr.write(
            "Input was {input_type}: {data}\nCodepoints: {codepoints}".format(
                input_type=input_type, data=data1, codepoints=codepoints))
        raise


def main():
    #atheris.instrument_all()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
