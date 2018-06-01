from json import dumps, loads
from glob import glob
import re
import sys
import numpy as np
import os
import multiprocessing
from multiprocessing import Pool
from functools import partial
import time
import itertools

# Number of sensors to compare each sensor with (= all sensors - 1)
NUM_SENSORS = 0

# Sensor mapping: car experiment
SENSORS_CAR1 = ['01', '02', '03', '04', '05', '06']
SENSORS_CAR2 = ['07', '08', '09', '10', '11', '12']

# Sensor mapping: office experiment
SENSORS_OFFICE1 = ['01', '02', '03', '04', '05', '06', '07', '08']
SENSORS_OFFICE2 = ['09', '10', '11', '12', '13', '14', '15', '16']
SENSORS_OFFICE3 = ['17', '18', '19', '20', '21', '22', '23', '24']

# List of sensor mappings
SENSORS = []

# Root path - points to the result folder of structure:
# /Sensor-xx/audio/<audio_features>/<time_intervals>
ROOT_PATH = ''

# Number of workers to be used in parallel
NUM_WORKERS = 0


def parse_folders(path, feature):
    # Local vars
    cur_folder = ''
    file_list = []
    folder_list = []

    # Iterate over matched files
    for json_file in glob(path, recursive=True):
        # Get the current folder, e.g. 10sec, 1min, etc.
        # (take different slashes into account: / or \)
        regex = re.escape(feature) + r'(?:/|\\)(.*)(?:/|\\)Sensor-'
        match = re.search(regex, json_file)

        # If there is no match - exit
        if not match:
            print('parse_folders: no match for the folder name, exiting...')
            sys.exit(0)

        # Check if the folder has changed - used for logging
        if len(cur_folder) > 0:
            if cur_folder != match.group(1):

                # Update current folder
                cur_folder = match.group(1)

                # Save the current file list to folder list
                folder_list.append(file_list)

                # Null file list
                file_list = []

                # Add first new element to file list
                file_list.append(json_file)

            else:
                file_list.append(json_file)
        else:
            cur_folder = match.group(1)
            file_list.append(json_file)

    # Take care of the last element
    if file_list:
        folder_list.append(file_list)

    return folder_list


# This function adds symmetry to Summary.json files generated by the resulting function
# from aggregate_results.py: aggregate_features()
def align_summary(path, feature_class):
    # Iterate over matched files
    for json_file in glob(path, recursive=True):
        # print('parsed file: ' + json_file)

        # Get target sensor number, e.g. 01, 02, etc.
        # (take different slashes into account: / or \)
        regex = r'Sensor-(.*)(?:/|\\)' + re.escape(feature_class) + r'(?:/|\\)'
        match = re.search(regex, json_file)

        # If there is no match - exit
        if not match:
            print('align_summary: no match for the sensor field, exiting...')
            sys.exit(0)

        # Construct target sensor string, e.g. Sensor-01, Sensor-02, etc.
        target_sensor = 'Sensor-' + match.group(1)

        # Open and read the JSON file
        with open(json_file, 'r') as f:
            json = loads(f.read())
            results = json['results']
            # Count the number of results
            res_len = len(results)

        # Check if the results are complete
        if res_len < NUM_SENSORS:
            # Get the number of sensor fields to be added
            res_count = NUM_SENSORS-res_len

            # Iterate over missing sensors
            for i in range(1, res_count + 1):
                # Make it 01, 02, etc.
                if i < 10:
                    insert_sensor = 'Sensor-' + '0' + str(i)
                else:
                    insert_sensor = 'Sensor-' + str(i)

                # Path of file to be parsed (take different slashes into account: / or \)
                regex = r'Sensor-(.*)(?:/|\\)' + re.escape(feature_class) + r'(?:/|\\)'
                sub_str = insert_sensor + '/' + feature_class + '/'
                sym_path = re.sub(regex, sub_str, json_file)
                # print('sym file: %s ---- with field: %s' % (sym_path, target_sensor.lower()))

                # Open and read JSON file
                with open(sym_path, 'r') as f:
                    sym_json = loads(f.read())
                    # Get the field to be symmetrically added to json_file
                    sym_field = sym_json['results'][target_sensor.lower()]

                # Add sym_field to results
                json['results'][insert_sensor.lower()] = sym_field

            # Save the updated json file
            with open(json_file, 'w') as f:
                f.write(dumps(json, indent=4, sort_keys=True))


# This function creates Summary.json for the last sensor (e.g. 12 - car, 24 - office)
# folders of which do not contain any results
def add_last_summary(path, feature, feature_class, summary_file):
    # Iterate over matched files
    for json_file in glob(path, recursive=True):

        # print('parsed file: ' + json_file)

        if feature != 'temp_hum_press_shrestha':
            # Get the current folder, e.g. 10sec, 1min, etc.
            # (take different slashes into account: / or \)
            regex = re.escape(feature) + r'(?:/|\\)(.*)(?:/|\\)'
            match = re.search(regex, json_file)

            # If there is no match - exit
            if not match:
                print('add_last_summary: no match for the folder name, exiting...')
                sys.exit(0)

            cur_folder = match.group(1)
        else:
            cur_folder = feature

        # Get target sensor number - the last one Sensor-12(car) or Sensor-24(office)
        # (take different slashes into account: / or \)
        regex = r'Sensor-(.*)(?:/|\\)' + re.escape(feature_class) + r'(?:/|\\)'
        match = re.search(regex, json_file)

        # If there is no match - exit /
        if not match:
            print('add_last_summary: no match for the sensor field, exiting...')
            sys.exit(0)

        # Construct target sensor string, e.g. Sensor-12(car) or Sensor-24(office)
        target_num = match.group(1)
        target_sensor = 'Sensor-' + target_num

        # Dictionary to store result fields
        json_dict = {}

        # Iterate over all sensors
        for i in range(1, NUM_SENSORS + 1):
            # Make it 01, 02, etc.
            if i < 10:
                insert_sensor = 'Sensor-' + '0' + str(i)
            else:
                insert_sensor = 'Sensor-' + str(i)

            # Path of file to be parsed (take different slashes into account: / or \)
            regex = r'Sensor-(.*)(?:/|\\)' + re.escape(feature_class) + r'(?:/|\\)'
            sub_str = insert_sensor + '/' + feature_class + '/'
            sym_path = re.sub(regex, sub_str, json_file) + summary_file
            # print('sym file: %s ---- with field: %s' % (sym_path, target_sensor.lower()))

            # Open and read JSON file
            with open(sym_path, 'r') as f:
                sym_json = loads(f.read())
                # Get the field to be symmetrically added to json_file
                sym_field = sym_json['results'][target_sensor.lower()]

            # Add sym_field to results
            json_dict[insert_sensor.lower()] = sym_field

        # Result that goes into JSON (name stolen from Max;))
        rv = {}

        # Metadata dict
        meta_dict = {}

        # Metadata fields: target sensor, feature, duration and value
        meta_dict['sensor'] = target_num
        meta_dict['feature'] = feature
        if cur_folder == feature:
            meta_dict['time_interval'] = 'n/a'
        else:
            meta_dict['time_interval'] = cur_folder

        if feature == 'audioFingerprint' or feature == 'noiseFingerprint':
            meta_dict['value'] = 'fingerprints_similarity_percent'
        elif feature == 'soundProofXcorr':
            meta_dict['value'] = 'max_xcorr'
        elif feature == 'timeFreqDistance':
            meta_dict['value'] = 'max_xcorr, time_freq_dist'
        elif feature == 'ble_wifi_truong' and feature_class == 'ble':
            meta_dict['value'] = 'euclidean, jaccard'
        elif feature == 'ble_wifi_truong' and feature_class == 'wifi':
            meta_dict['value'] = 'euclidean, jaccard, mean_exp, mean_hamming, sum_squared_ranks'
        elif feature == 'temp_hum_press_shrestha':
            meta_dict['value'] = 'hamming_dist'

        # Add metadata
        rv['metadata'] = meta_dict

        # Add results
        rv['results'] = json_dict

        filename = json_file + summary_file
        # print('Saving a file: %s' % filename)
        # Save the new JSON file
        with open(filename, 'w') as f:
            f.write(dumps(rv, indent=4, sort_keys=True))


# ToDo: switch to gz json files
def process_power(file_list, feature=''):

    # Get the current folder, e.g. 10sec, 1min, etc.
    # (take different slashes into account: / or \)
    regex = re.escape(feature) + r'(?:/|\\)(.*)(?:/|\\)Sensor-'
    match = re.search(regex, file_list[0])

    # If there is no match - exit
    if not match:
        print('process_power: no match for the folder name, exiting...')
        sys.exit(0)

    cur_folder = match.group(1)

    # Get the base path
    match = re.search(r'(.*)Sensor-', file_list[0])

    # If there is no match - exit
    if not match:
        print('process_power: no match for the log path, exiting...')
        sys.exit(0)

    base_path = match.group(1)

    for json_file in file_list:

        # Get the sensor number, e.g. 01, 02, etc.
        # (take different slashes into account: / or \)
        regex = re.escape(cur_folder) + r'(?:/|\\)Sensor-(.*).json'
        match = re.search(regex, json_file)

        # If there is no match - exit
        if not match:
            print('process_power: no match for the file name, exiting...')
            sys.exit(0)

        # Construct path to the Power-*.json file
        power_file = base_path + 'Power-' + match.group(1) + '.json'

        # Add power from Power-*.json to Sensor-*.json and remove the former file
        add_spf_power(json_file, power_file)


def add_spf_power(json_file, power_file):

    # Open and read data JSON file
    with open(json_file, 'r') as f:
        json_data = loads(f.read())
        data_res = json_data['results']
        metadata = json_data['metadata']
        # Count the number of results
        res_data_len = len(data_res)

    # Open and read power JSON file
    with open(power_file, 'r') as f:
        json_power = loads(f.read().replace('-Inf', '-Infinity'))
        power_res = json_power['results']
        # Count the number of results
        res_power_len = len(power_res)

    if res_data_len != res_power_len:
        print('add_spf_power: length mismatch between %s and %s --- exiting...' \
              % (json_file, power_file))
        sys.exit(0)

    # List to store power values
    power_list = []

    # Store power values in the power list
    for k, v in sorted(power_res.items()):
        power_list.append(v)

    # Index to iterate over the power_list
    idx = 0

    # Iterate over the data_res dictionary and add power values from power_list to data_res (sigh!)
    for k, v in sorted(data_res.items()):
        for k1, v1 in sorted(power_list[idx].items()):
            v[k1] = v1
        idx += 1

    # Result that goes into JSON (name stolen from Max;))
    rv = {}

    # Add metadata
    rv['metadata'] = metadata

    # Add results
    rv['results'] = data_res

    # Save the result back to json_file
    with open(json_file, 'w') as f:
        f.write(dumps(rv, indent=4, sort_keys=True))

    # Delete Power-*.json file
    os.remove(power_file)


def wrap_up_summary(path):
    # Iterate over matched files
    for json_file in glob(path, recursive=True):

        co_located_list = []
        non_colocated_list = []

        # Open and read JSON file
        with open(json_file, 'r') as f:
            json = loads(f.read())
            results = json['results']
            metadata = json['metadata']

        # Get the target sensor
        target_sensor = metadata['sensor']

        # Make a copy of list of sensors' lists
        sensors_lists = list(SENSORS)

        # Iterate over list of sensors' lists
        for sensor_list in SENSORS:
            # Check if target sensor is in sensor_list
            if target_sensor in sensor_list:
                # Construct co-located list excluding target sensor
                co_located_list = list(sensor_list)
                co_located_list.remove(target_sensor)

                # Construct non-colocated list
                sensors_lists.remove(sensor_list)
                non_colocated_list = list(itertools.chain.from_iterable(sensors_lists))

                # Get out from the loop
                break

        # Lists of co-located and non-colocated values
        co_located_val = []
        non_colocated_val = []

        # Accumulate co-located and non-colocated values
        for k, v in sorted(results.items()):
            # Get the sensor number, e.g. 01, 02, etc.
            sensor_num = k.split('-')[1]

            if sensor_num in co_located_list:
                co_located_val.append(v)
            else:
                non_colocated_val.append(v)

        # Get names of feature keys
        feature_keys = list(co_located_val[0].keys())

        # Sort feature_keys
        feature_keys.sort()

        # Dictionaries of co-located and non-colocated results
        co_located_dict = {}
        non_colocated_dict = {}

        for feature_key in feature_keys:
            result_list = wrap_up_feature(co_located_val, non_colocated_val, feature_key)
            co_located_dict[feature_key] = result_list[0]
            non_colocated_dict[feature_key] = result_list[1]

        # Append co-located and non-colocated sensor lists
        co_located_dict['_sensors'] = co_located_list
        non_colocated_dict['_sensors'] = non_colocated_list

        # Add new fields to the results
        json['results']['co_located'] = co_located_dict
        json['results']['non_colocated'] = non_colocated_dict

        # Save the updated JSON file
        with open(json_file, 'w') as f:
            f.write(dumps(json, indent=4, sort_keys=True))


def wrap_up_feature(co_located_val, non_colocated_val, feature_key):

    if isinstance(co_located_val[0][feature_key], float):
        # List to store feature metrics, e.g. mean, max, threshold_percent
        feature_metric_list = []
    elif isinstance(co_located_val[0][feature_key], dict):
        # List to store feature metrics, e.g. mean, max, threshold_percent
        feature_metric_list = list(co_located_val[0][feature_key].keys())
        feature_metric_list.sort()
    elif isinstance(co_located_val[0][feature_key], str):
        if co_located_val[0][feature_key] == 'no overlap':
            result_list = ['no overlap', 'no overlap']
            return result_list
    else:
        print('wrap_up_feature: instance of feature: %s must be dict or float --- exiting...' %
              co_located_val[0][feature_key])
        sys.exit(0)

    # Initialize list of lists for feature metrics
    co_located_lists = [[] for i in range(len(feature_metric_list))]
    non_colocated_lists = [[] for i in range(len(feature_metric_list))]

    # Get co-located values
    for val in co_located_val:
        feature_metrics = val[feature_key]
        # Consider only meaningful values (discard no overlap fields)
        if feature_metrics != 'no overlap':
            if isinstance(feature_metrics, float):
                co_located_lists.append(feature_metrics)
            else:
                idx = 0
                for feature_metric in feature_metric_list:
                    co_located_lists[idx].append(feature_metrics[feature_metric])
                    idx += 1

    # Get non-colocated values
    for val in non_colocated_val:
        feature_metrics = val[feature_key]
        # Consider only meaningful values (discard no overlap fields)
        if feature_metrics != 'no overlap':
            if isinstance(feature_metrics, float):
                non_colocated_lists.append(feature_metrics)
            else:
                idx = 0
                for feature_metric in feature_metric_list:
                    non_colocated_lists[idx].append(feature_metrics[feature_metric])
                    idx += 1

    # Dictionaries of co-located and non-colocated results
    co_located_dict = {}
    non_colocated_dict = {}

    # Check if co_located_lists is a simple list or list of lists
    if isinstance(co_located_lists[0], float):

        # Convert co-located and non-colocated values to np arrays
        co_located_array = np.array(list(co_located_lists), dtype=float)
        non_colocated_array = np.array(list(non_colocated_lists), dtype=float)

        # Compute mean, median, std, min, max, q1, q3 for co-located array
        co_located_dict = compute_metrics(co_located_array)

        # Compute mean, median, std, min, max, q1, q3 for non-colocated array
        non_colocated_dict = compute_metrics(non_colocated_array)

    else:
        # Iterate over feature metrics
        idx = 0
        for feature_metric in feature_metric_list:
            # Convert both co-located and non-colocated feature metrics to np arrays
            co_located_array = np.array(list(co_located_lists[idx]), dtype=float)
            non_colocated_array = np.array(list(non_colocated_lists[idx]), dtype=float)

            # Compute mean, median, std, min, max, q1, q3 for co-located array
            co_located_metric = compute_metrics(co_located_array)

            # Compute mean, median, std, min, max, q1, q3 for non-colocated array
            non_colocated_metric = compute_metrics(non_colocated_array)

            # Store metrics in dictionaries
            co_located_dict[feature_metric] = co_located_metric
            non_colocated_dict[feature_metric] = non_colocated_metric

            idx += 1

    # Result list to be returned
    result_list = [co_located_dict, non_colocated_dict]

    return result_list


def compute_metrics(feature_np_array):
    # Dictionary to store the results of metric computation
    feature_dict = {}

    # Compute mean, median, std, min, max, q1, q3 and store results in feature_dict
    feature_dict['mean'] = np.mean(feature_np_array)
    feature_dict['median'] = np.median(feature_np_array)
    feature_dict['std'] = np.std(feature_np_array)
    feature_dict['min'] = np.amin(feature_np_array)
    feature_dict['max'] = np.amax(feature_np_array)
    feature_dict['q1'] = np.percentile(feature_np_array, 25)
    feature_dict['q3'] = np.percentile(feature_np_array, 75)

    return feature_dict


# ToDo: switch to gz json files
def format_power():

    # Audio feature
    feature = 'soundProofXcorr'

    # Path to result data files
    feature_path = ROOT_PATH + 'Sensor-*/audio/' + feature + '/*/Sensor-*.json'

    # Get the list of JSON files for each timeInterval folder, e.g. 5sec, 1min, etc.
    folder_list = parse_folders(feature_path, feature)

    # Sort results of folder_list
    for file_list in folder_list:
        file_list.sort()

    # Check if the folder list was successfully created
    if not folder_list:
        print('format_power: Folder list is empty, exiting...')
        sys.exit(0)

    # Initiate a pool of workers
    pool = Pool(processes=NUM_WORKERS, maxtasksperchild=1)

    # Use partial to pass a static feature parameter
    func = partial(process_power, feature=feature)

    # Let workers do the job
    pool.imap(func, folder_list)

    # Wait for processes to terminate
    pool.close()
    pool.join()


def format_interval_features(feature, feature_class, summary_file):

    # Path to summary.json files
    feature_summary = ROOT_PATH + 'Sensor-*/' + feature_class + '/' + feature + \
                      '/*/' + summary_file
    last_feature_summary = ROOT_PATH + 'Sensor-' + str(NUM_SENSORS + 1) + \
                           '/' + feature_class + '/' + feature + '/*/'

    # Format summary results
    align_summary(feature_summary, feature_class)
    add_last_summary(last_feature_summary, feature, feature_class, summary_file)

    # Wrap up summary: overview of co-located vs. non-colocated
    wrap_up_summary(feature_summary)


def format_non_interval_features(feature, feature_class, summary_file):

    # Path to summary.json files
    feature_summary = ROOT_PATH + 'Sensor-*/' + feature_class + '/' + feature + \
                      '/' +  summary_file
    last_feature_summary = ROOT_PATH + 'Sensor-' + str(NUM_SENSORS + 1) +\
                           '/' + feature_class + '/' + feature + '/'

    # Format summary results
    align_summary(feature_summary, feature_class)
    add_last_summary(last_feature_summary, feature, feature_class, summary_file)

    # Wrap up summary: overview of co-located vs. non-colocated
    wrap_up_summary(feature_summary)


def format_features(summary_file):

    # Audio feature
    feature = 'audioFingerprint'

    # Feature class
    feature_class = 'audio'

    # Format AFP
    print('formatting AFP...')
    format_interval_features(feature, feature_class, summary_file)

    # Audio feature
    feature = 'noiseFingerprint'

    # Format NFP
    print('formatting NFP...')
    format_interval_features(feature, feature_class, summary_file)

    # Audio feature
    feature = 'soundProofXcorr'

    # Format SPF
    print('formatting SPF...')
    format_interval_features(feature, feature_class, summary_file)

    # Audio feature
    feature = 'timeFreqDistance'

    # Format TFD
    print('formatting TFD...')
    format_interval_features(feature, feature_class, summary_file)

    # BLE feature
    feature = 'ble_wifi_truong'

    # Feature class
    feature_class = 'ble'

    # Format BLE
    print('formatting ble...')
    format_interval_features(feature, feature_class, summary_file)

    # Feature class
    feature_class = 'wifi'

    # Format Wi-fi
    print('formatting wifi...')
    format_interval_features(feature, feature_class, summary_file)

    # PHY feature
    feature = 'temp_hum_press_shrestha'

    # Feature class
    feature_class = 'temp'

    # Format temperature
    print('formatting temp...')
    format_non_interval_features(feature, feature_class, summary_file)

    # Feature class
    feature_class = 'hum'

    # Format humidity
    print('formatting hum...')
    format_non_interval_features(feature, feature_class, summary_file)

    # Feature class
    feature_class = 'press'

    # Format pressure
    print('formatting press...')
    format_non_interval_features(feature, feature_class, summary_file)


if __name__ == '__main__':
    # Check the number of input args
    if len(sys.argv) == 4:
        # Assign input args
        ROOT_PATH = sys.argv[1]
        scenario = sys.argv[2]
        sub_scenario = sys.argv[3]

    elif len(sys.argv) == 5:
        # Assign input args
        ROOT_PATH = sys.argv[1]
        scenario = sys.argv[2]
        sub_scenario = sys.argv[3]
        NUM_WORKERS = sys.argv[4]

        # Check if <num_workers> is an integer more than 2
        try:
            NUM_WORKERS = int(NUM_WORKERS)
            if NUM_WORKERS < 2:
                print('Error: <num_workers> must be a positive number > 1!')
                sys.exit(0)
        except ValueError:
            print('Error: <num_workers> must be a positive number > 1!')
            sys.exit(0)
    else:
        print('Usage: format_results.py <root_path> <scenario> <sub_scenario> (optional - <num_workers>)')
        sys.exit(0)

    # Get the number of cores on the system
    num_cores = multiprocessing.cpu_count()

    # Set the number of workers
    if NUM_WORKERS == 0:
        NUM_WORKERS = num_cores
    elif NUM_WORKERS > num_cores:
        NUM_WORKERS = num_cores

    # Check if <root_path> is a valid path
    if not os.path.exists(ROOT_PATH):
        print('Error: Root path "%s" does not exist!' % ROOT_PATH)
        sys.exit(0)

    # Check if we have a slash at the end of the <root_path>
    if ROOT_PATH[-1] != '/':
        ROOT_PATH = ROOT_PATH + '/'

    # Check if <scenario> is a string 'power', 'car' or 'office'
    if scenario == 'power':
        # Format power
        start_time = time.time()
        print('Formatting power using %d workers...' % NUM_WORKERS)
        format_power()
        print('--- %s seconds ---' % (time.time() - start_time))
    elif scenario == 'car':
        NUM_SENSORS = 11
        SENSORS.append(SENSORS_CAR1)
        SENSORS.append(SENSORS_CAR2)

        # Check <sub_scenario>
        if sub_scenario == 'all':
            # Format features
            format_features('Summary.json')
        elif sub_scenario == 'city':
            # Format features
            format_features('Summary-city.json')
        elif sub_scenario == 'highway':
            # Format features
            format_features('Summary-highway.json')
        elif sub_scenario == 'static':
            # Format features
            format_features('Summary-static.json')
        else:
            print('Error: <sub_scenario> for the car scenario can only be "all", "city", "highway" or "static"!')
            sys.exit(0)

    elif scenario == 'office':
        NUM_SENSORS = 23
        SENSORS.append(SENSORS_OFFICE1)
        SENSORS.append(SENSORS_OFFICE2)
        SENSORS.append(SENSORS_OFFICE3)

        # Check <sub_scenario>
        if sub_scenario == 'all':
            # Format features
            format_features('Summary.json')
        elif sub_scenario == 'night':
            # Format features
            format_features('Summary-night.json')
        elif sub_scenario == 'weekday':
            # Format features
            format_features('Summary-weekday.json')
        elif sub_scenario == 'weekend':
            # Format features
            format_features('Summary-weekend.json')
        else:
            print('Error: <sub_scenario> for the office scenario can only be "all", "night", "weekday" or "weekend"!')
            sys.exit(0)
    else:
        print('Error: <scenario> can only be "power", "car" or "office"!')
        sys.exit(0)
