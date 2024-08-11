def generate_filenames(original_filename, num_files):
    base_name = original_filename.rsplit(".", 1)[0]  # Remove the file extension
    extension = original_filename.rsplit(".", 1)[-1]  # Get the file extension

    filenames = []
    for i in range(num_files):
        new_filename = f"{base_name}_crop_{i+1}.{extension}"
        filenames.append(new_filename)

    return filenames


def insert_filenames_into_response(blueprint, filenames, imagename):
    slots = blueprint.get("slots", [])

    blueprint["file_name"] = imagename
    
    for i, slot in enumerate(slots):
        if i < len(filenames):
            slot["file_name"] = filenames[i]

    blueprint["slots"] = slots
    return blueprint


def update_response_with_crops(blueprint, cropped_images):
    slots = blueprint.get("slots", [])

    for i, slot in enumerate(slots):
        # Update the slot with the corresponding cropped image (ROI)
        if i < len(cropped_images):
            slot["roi"] = cropped_images[i]

    blueprint["slots"] = slots
    return blueprint
