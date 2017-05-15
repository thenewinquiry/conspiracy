before installing requirements, install `dlib` dependencies:

    sudo apt-get install build-essential cmake libgtk-3-dev libboost-all-dev -y

to setup `darknet`:

    git clone git@github.com:thtrieu/darkflow.git
    cd darkflow
    python3 setup.py build_ext --inplace
    pip install -e .

the model weights are linked to in that repo.

`facenet.py` is from <https://github.com/davidsandberg/facenet>. the model weights are linked to in that repo as well.

this expects to be registered as a listener for [`reality`](https://github.com/frnsys/reality), which creates a FIFO file (`fifo`) that `main.py` polls for new articles to process.