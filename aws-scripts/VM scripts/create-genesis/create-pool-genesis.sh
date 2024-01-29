#!/bin/bash

echo "Creating node.csv files...."


# Define the header file and output file
header_file="header.csv"
output_file="nodes.csv"
bucket_name="your_bucket_name" # replace with your bucket name

# Copy the header file to the output file
cp $header_file $output_file

# Iterate over each node file, fetch it from S3, and append it to the output file
for i in {1..7}
do
    aws s3 cp "s3://$bucket_name/node${i}.csv" ./
    cat "node${i}.csv" >> $output_file
done


echo "Done!"