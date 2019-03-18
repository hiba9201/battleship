

class Field:
    @staticmethod
    def create_field(x=10, y=10):
        field = []
        for i in range(x):
            field.append([])
            for j in range(y):
                field[i].append(False)
        return field
