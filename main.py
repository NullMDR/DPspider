from city import City


def main():
    to_request = ['北京', '上海']
    for city_name in to_request:
        print(city_name)
        city = City(city_name)
        city.get()
        print(city_name, city.id)


if __name__ == '__main__':
    main()