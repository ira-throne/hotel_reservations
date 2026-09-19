# Hotel Revenue by Month with MapReduce

This project uses MapReduce to rank every month from 2015 to 2018 by hotel booking revenue. The hotel company changed how it stored its data partway through, so the revenue has to be computed from two datasets with different schemas. The job reconciles both formats in a single pass, splits stays that span multiple months, and outputs each month/year combination sorted by revenue.

The job is written in Python with the [mrjob](https://mrjob.readthedocs.io/) library and runs on Hadoop, or locally without Hadoop.

## Datasets

| | `hotel-booking.csv` | `customer-reservations.csv` |
|---|---|---|
| Years covered | 2015 to 2016 | 2017 to 2018 |
| Columns | 13 | 10 |
| Month format | Name (`July`) | Number (`7`) |
| Cancellation flag | `0` / `1` | `Not_Canceled` / `Canceled` |

Both datasets record the arrival date, the number of weekend and weekday nights, and the average price per night, which is everything needed to compute revenue.

## Workflow

The job runs in two MapReduce steps.

**Step 1: mapper.** Each line is split on commas, and the column count identifies which dataset it came from (13 for hotel bookings, 10 for customer reservations). Canceled reservations are skipped, since they bring in no revenue. For the rest, the mapper converts month names to numbers, computes the length of stay, and emits the month/year as the key and the revenue as the value.

Stays that cross into another month are split between them. For example, a 7-night stay starting June 27 contributes 4 nights of revenue to June and 3 to July. The mapper accounts for 30- and 31-day months, leap years, and stays that roll over from December into the next year.

**Step 1: combiner.** Sums the revenue for each month/year within a mapper's output before it's sent to the reducer, reducing the amount of data shuffled between nodes.

**Step 1: reducer.** Sums the revenue for each month/year across all mappers and emits every result under a single key, so the next step receives them all together.

**Step 2: reducer.** Sorts all month/year totals by revenue in descending order and rounds them to two decimals.

## Results

The output contains 38 month/year combinations. The top 10:

| Rank | Month | Revenue |
|---|---|---|
| 1 | August 2016 | 1,822,416.64 |
| 2 | July 2016 | 1,512,810.62 |
| 3 | September 2016 | 1,309,432.06 |
| 4 | August 2015 | 1,129,153.72 |
| 5 | June 2016 | 1,122,601.30 |
| 6 | October 2016 | 1,094,761.78 |
| 7 | September 2015 | 1,075,243.53 |
| 8 | May 2016 | 1,058,766.78 |
| 9 | April 2016 | 885,728.58 |
| 10 | October 2015 | 813,698.33 |

Summer and early fall are consistently the strongest months. The customer-reservations data starts in July 2017, so there's no revenue for February through June 2017. The small totals for January 2017 and January 2019 are stays that began in December and rolled over into the new year.

## Running the project

### Locally, without Hadoop

mrjob can run the job in plain Python, which is the quickest way to try it.

```bash
pip install mrjob
python3 mrjob_script.py customer-reservations.csv hotel-booking.csv > output.txt
```

### On Hadoop

With Hadoop running, upload both CSVs to HDFS:

```bash
hadoop fs -mkdir /project
hadoop fs -put hotel-booking.csv /project
hadoop fs -put customer-reservations.csv /project
```

Then run the script:

```bash
./main.sh
```

It prompts for three paths in `hdfs:///foldername` format, without a trailing slash:

1. the folder containing `customer-reservations.csv` (e.g. `hdfs:///project`)
2. the folder containing `hotel-booking.csv` (e.g. `hdfs:///project`)
3. a new output folder (e.g. `hdfs:///output`), which must not already exist

To view the results:

```bash
hadoop fs -cat hdfs:///output/part-*
```

`shell_commands` has the full sequence, including resetting HDFS and starting and stopping Hadoop.

## Files

- `mrjob_script.py`: the MapReduce job
- `main.sh`: prompts for input and output paths and runs the job on Hadoop
- `shell_commands`: step-by-step Hadoop setup and run commands
