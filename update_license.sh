#! /bin/bash

if [ -z "$1" ]; then
	echo "Please add path to the file contents"
	echo "Use -h or --help to get info"
	exit 1
fi

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
	echo "Usage: update_license.sh [LICENSE_FILE] [CODE_FOLDER]"
	echo "Command line utility for updating the license in every file of the selected directory"
	exit 0
fi

if [ -z "$2" ]; then
	echo "Please add folder path, which contains python files to be updated"
	echo "Use -h or --help to get info"
	exit 2
fi

LICENSE_CONTENTS="$(cat $1)"
UPDATE_FOLDER=$2

if [ -z "$LICENSE_CONTENTS" ]; then
	echo "License file is empty"
	exit 3
fi

# Making in-file license
LICENSE_LENGTH=$(wc -L < $1)
LICENSE_HEADER=$(printf %$(($LICENSE_LENGTH/2-4))s | tr " " "=")
LICENSE_HEADER="$LICENSE_HEADER LICENSE "
LICENSE_HEADER_RIGHT=$(printf %$(($LICENSE_LENGTH-${#LICENSE_HEADER}))s | tr " " "=")
LICENSE_HEADER="$LICENSE_HEADER$LICENSE_HEADER_RIGHT"
LICENSE_FOOTER=$(printf %$(($LICENSE_LENGTH))s | tr " " "=")
LICENSE_CONTENTS="\"""\"""\"""
$LICENSE_HEADER
${LICENSE_CONTENTS}
$LICENSE_FOOTER
"

echo "$LICENSE_CONTENTS"

for f in $(find $UPDATE_FOLDER -name "*.py")
do
	echo $f
	FILE_CONTENTS=$(cat $f)
	if [ "${FILE_CONTENTS:0:3}" == '"""' ]; then
		LICENSE_END=$(echo "$FILE_CONTENTS" | grep -nE "^(=)+$" | cut -f1 -d:)
		if [ -z "$LICENSE_END" ]; then
			FILE_CONTENTS="$LICENSE_CONTENTS
${FILE_CONTENTS:3}"
			echo "$FILE_CONTENTS" > $f
			echo "License added to the existing file docstring"
		else
			((++LICENSE_END))
			FILE_CONTENTS="$LICENSE_CONTENTS$(echo "$FILE_CONTENTS" | tail -n +$LICENSE_END)"
			echo "$FILE_CONTENTS" > $f
			echo "License updated"
		fi
		LICENSE_END=""
	else
		FILE_CONTENTS="$LICENSE_CONTENTS"\"""\"""\""
$FILE_CONTENTS"
		echo "$FILE_CONTENTS" > $f
		echo "License added"
	fi
done

