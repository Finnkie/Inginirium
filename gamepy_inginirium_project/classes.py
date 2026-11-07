class Phone:
    color = "black"
    battery = 100

    def take_photo(self):
        print("Фото сделано!")
        self.battery = -5
        if self.battery <= 20:
            print("Заряд кончается!")
