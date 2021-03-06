# conspiracy

machine and human apophenia

created for [The New Inquiry](https://thenewinquiry.com/)'s [_Conspiracy_ issue](https://thenewinquiry.com/magazine/conspiracy)

[view it live here](https://conspiracy.thenewinquiry.com/)

## setup

before installing requirements, install `dlib` dependencies:

    sudo apt-get install build-essential cmake libgtk-3-dev libboost-all-dev -y

to setup `darknet` (for the [yolo object recognition model](https://pjreddie.com/darknet/yolo/)):

    git clone git@github.com:thtrieu/darkflow.git
    cd darkflow
    python3 setup.py build_ext --inplace
    pip install -e .

the model weights are linked to in that repo.

`facenet.py` is from <https://github.com/davidsandberg/facenet>. the model weights are linked to in that repo as well.

`phantomjs` is necessary to screenshot websites. download from:

    wget -O phantomjs.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    tar jxf phantomjs.tar.bz2
    sudo mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

`tesseract` for OCR:

    sudo apt-get install tesseract-ocr

many images are sourced from wikipedia commons. you can grab the latest dump here: <https://dumps.wikimedia.org/commonswiki/latest/commonswiki-latest-image.sql.gz>, extract it to `assets/commonswiki-latest-image.sql`, then run `parse_images_dump.py` from that directory to build image urls from the dump. this will take a long time

note that this doesn't download the images. you can download a random sample of these commons urls like so:

```python
from images import sampler
sampler.fetch_sample(100)
```

this program expects to be registered as a listener for [`reality`](https://github.com/frnsys/reality), which creates a FIFO file (`fifo`) that `main.py` polls for new articles to process. run `listen.py` to listen to the FIFO queue and automatically run object/face detection on new images.

## conspire

to generate a conspiracy, run `generate.py`.

you can view the latest conspiracy by running an HTTP server from `public/`, e.g.:

    cd public
    python3 -m http.server
