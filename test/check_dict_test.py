def is_subset(sub_dict, super_dict):
    for key, value in sub_dict.items():
        if key not in super_dict:
            return False
        if isinstance(value, dict):
            if not isinstance(super_dict[key], dict):
                return False
            if not is_subset(value, super_dict[key]):
                return False
        else:
            if super_dict[key] != value:
                return False
    return True

a = {}
b = {"a": "b", "c": {"f": "g"}}

result = is_subset(b, a)
print(result)