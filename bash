#!/bin/bash
IFS='.' read -a array <<< $1;
for index in "${!array[@]}"
do
    echo "$index ${array[index]}"
done
echo $(ls)
filename="${array[0]}"
ext="${array[-1]}"

echo $("ffmpeg -i ./$1 -vf \"drawtext=fontfile=Arial.ttf: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontcolor=white: box=1: boxcolor=0x00000099\" -y ${filename}_numbered.${ext}")
