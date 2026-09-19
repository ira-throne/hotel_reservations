#!/bin/bash

# Taking input for input and output folders
read -p "Input the location of the customer-reservations.csv file: " cust_res_dir
read -p "Input the location of the hotel-booking.csv file: " hot_book_dir
read -p "Input the path to the output directory: " output_dir

# Executing the mapreduce
python3 mrjob_script.py -r hadoop "${cust_res_dir}/customer-reservations.csv" "${hot_book_dir}/hotel-booking.csv" --output-dir "${output_dir}"
