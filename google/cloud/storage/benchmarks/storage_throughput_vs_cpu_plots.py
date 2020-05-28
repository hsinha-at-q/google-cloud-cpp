#!/usr/bin/env python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Summarize the results from running storage_throughput_vs_cpu_benchmark."""

# These funny `%%` comments help if you load this script in Spyder
# (https://www.spyder-ide.org/). Each one starts a `cell` that you can
# manually execute.

# %%
import argparse
import pandas as pd
import plotnine as p9


# %%
def load_throughput_vs_cpu_output(file):
    """Loads the output generated by storage_storage_vs_cpu into a data frame."""
    df = pd.read_csv(file, comment="#", sep=",", header=0)
    df["MiB"] = df.ObjectSize / 1024 / 1024
    df["KiB"] = df.ObjectSize / 1024
    df["ElapsedSeconds"] = df.ElapsedTimeUs / 1_000_000
    df["MiBs"] = df.MiB / df.ElapsedSeconds
    df["CpuNanosPerByte"] = (df.CpuTimeUs * 1_1000) / df.ObjectSize
    return df


parser = argparse.ArgumentParser()
parser.add_argument(
    "--input-file",
    type=argparse.FileType("r"),
    required=True,
    help="load data from this file, should be the output of the storage_throughput_vs_cpu_benchmark",
)
parser.add_argument(
    "--output-prefix", type=str, required=True, help="prefix plot files with this name"
)
args = parser.parse_args()

# %%
data = load_throughput_vs_cpu_output(args.input_file)

# %%
print(data.head())

# %%
print(data.describe())

# %%
(
    p9.ggplot(data=data, mapping=p9.aes(x="KiB", y="ElapsedSeconds", color="ApiName"))
    + p9.geom_point()
    + p9.facet_grid("OpName ~ Crc32cEnabled + MD5Enabled", labeller="label_both")
    + p9.scale_y_log10()
).save(args.output_prefix + ".elapsed-vs-size.png")

# %%
(
    p9.ggplot(data=data, mapping=p9.aes(x="KiB", y="CpuNanosPerByte", color="ApiName"))
    + p9.geom_point()
    + p9.facet_grid("OpName ~ Crc32cEnabled + MD5Enabled", labeller="label_both")
    + p9.scale_y_log10()
).save(args.output_prefix + ".cpu-vs-size.png")