
# DeOldify

### Citation
원본 github : https://github.com/jantic/DeOldify

### Prepare:

```
# 만약 안된다면 env.yml 사용
conda env create -f environment.yml


# image model
mkdir models
wget https://www.dropbox.com/s/mwjep3vyqk5mkjc/ColorizeStable_gen.pth?dl=0 -O ./models/ColorizeStable_gen.pth

# video model
wget https://www.dropbox.com/s/336vn9y4qwyg9yz/ColorizeVideo_gen.pth?dl=0 -O ./models/ColorizeVideo_gen.pth

wget https://media.githubusercontent.com/media/jantic/DeOldify/master/resource_images/watermark.png -O ./resource_images/watermark.png

```


### Inference

```
# image colorize
python image_colorize.py --in_file [image file path] --out_file [output file path] --gpu [gpu0, gpu1, cpu...]

```






Follow [#DeOldify](https://twitter.com/search?q=%23Deoldify) or [Jason Antic](https://twitter.com/citnaj) on Twitter.

## License

All code in this repository is under the MIT license as specified by the LICENSE file.

The model weights listed in this readme under the "Pretrained Weights" section are trained by ourselves and are released under the MIT license.
