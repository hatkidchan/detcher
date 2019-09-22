image = shift_channels(image,
  shift_r = randint(-10, 10, 2) * 2,
  crop = True)

image = crt(image, (4, 4), (1.0, 0.7))

