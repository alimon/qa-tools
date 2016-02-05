#!/bin/bash

base_work_dir=/tmp
work_dir=$base_work_dir/toaster
poky_dir=$work_dir/poky
poky_url=git://git.yoctoproject.org/poky.git

if [ -d $work_dir ]; then
	rm -rf $work_dir
fi

mkdir -p $work_dir
git clone git://git.yoctoproject.org/poky.git $poky_dir

cd $poky_dir
virtualenv $poky_dir/venv
. $poky_dir/venv/bin/activate
. $poky_dir/oe-init-build-env
pip install -r $poky_dir/bitbake/toaster-requirements.txt
TOASTER_CONF=$poky_dir/meta-yocto/conf/toasterconf.json . $poky_dir/bitbake/bin/toaster start
