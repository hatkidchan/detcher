image = overlay(image,
  offset = (10, 10),
  opacity = 0.2,
  crop = False)

image = shift_channels(image,
  shift_r = (-20, -20),
  crop = True)

image = grayscale(image,
  factor = 0.8)

for _ in range(randint(5, 10)):
  start = randint(0, image.height)
  end = randint(20, 50) + start
  image = shift_auto(image, "horiz",
    start, end,
    lambda y: (y % 20) * 2)

image = noise(image)

image = crt(image, 
  step = (5, 5),
  values = (1.0, 0.5),
  fill = None)

