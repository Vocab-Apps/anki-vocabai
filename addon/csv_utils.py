import csv
import tempfile

def create_csv_without_header(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
            writer = csv.writer(temp_file)
            for row in reader:
                writer.writerow(row)
            return temp_file

def get_fieldnames(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        return header

def get_fieldname_to_index(csv_file_path: str):
    # get the list of fields in the csv_file_path CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_header = csv_file.readline()
        csv_fields = csv_header.split(',')
        csv_fields = [x.strip() for x in csv_fields]

        # create dict which maps field name to field index
        field_name_to_index = {field_name: index for index, field_name in enumerate(csv_fields)}
        return field_name_to_index            