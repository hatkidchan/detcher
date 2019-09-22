image = overlay(image,
  offset = (10, 10),
  opacity = 0.2)

image = shift_channels(image,
  shift_r = (20, 20),
  crop = False)

image = grayscale(image,
  factor = 0.8)

for _ in range(randint(5, 10)):
  start = randint(0, image.height)
  end = randint(20, 50) + start
  image = shift_auto(image, "horiz",
    start, end,
    lambda y: (sin(y / 10) * cos(y / 20) * 40) % 20)

image = crt(image, 
  step = (5, 5),
  values = (1.0, 0.7),
  fill = None)

