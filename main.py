from pygame.locals import *
import pygame, collections, random, time, itertools

WINDOW_SIZE = (1200, 800)
DISPLAY_SIZE = (WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)

UP, LEFT, RIGHT, DOWN = (0, -1), (-1, 0), (1, 0), (0, 1)

clock = pygame.time.Clock()


class Food:
    x = 0
    y = 0
    texture_size = 0

    def __init__(self, x, y, *, texture_size):
        self.x, self.y = x, y
        self.texture_size = texture_size

    # function to draw food
    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))

    def __repr__(self):
        return (
            "Food{" + f"x={self.x}, y={self.y}, texture_size={self.texture_size}" + "}"
        )


class Animation:
    tick = 0
    playing = False
    counter = 0


class GrowingAnimation(Animation):
    def __init__(self, player, border):
        self.player = player
        self.border = border

    def play(self):
        if not self.playing:
            return False

        if self.tick > 20:
            self.tick = 0
            self.playing = False
            # the playing flag will effect the animation next tick
            return True
        if self.tick == 0:
            self.counter = 0

        default_snake_size = self.player.SNAKE_BODY_IMAGE.get_size()

        stop_snake_movement = False
        if self.tick > 15:
            self.border.shrink_border(1)
            new_snake_size = (
                default_snake_size[0],
                default_snake_size[1],
            )
        elif self.tick > 10:
            new_snake_size = (
                default_snake_size[0] * 2,
                default_snake_size[1] * 2,
            )
        else:
            new_snake_size = (default_snake_size[0] * 2, default_snake_size[1] * 2)
            stop_snake_movement = True
        # get big for 2 ticks and small for 2 ticks
        snake_body_image = None
        snake_head_image = None
        if self.counter < 2 or self.tick > 10:
            snake_body_image = pygame.transform.scale(
                self.player.SNAKE_BODY_IMAGE,
                new_snake_size,
            )
            snake_head_image = pygame.transform.scale(
                self.player.SNAKE_HEAD_IMAGE,
                new_snake_size,
            )
        else:
            if self.counter == 4:
                self.counter = 0

        # make sure the snake is facing the right direction
        self.player.rotate_snake_texture(
            self.player.rotation,
            default_body_image=snake_body_image,
            default_head_image=snake_head_image,
        )

        self.tick += 1
        self.counter += 1

        return stop_snake_movement


class Border:
    top_left = (0, 0)
    top_right = (DISPLAY_SIZE[0], 0)
    bottom_left = (0, DISPLAY_SIZE[1])
    bottom_right = DISPLAY_SIZE
    color = (0, 0, 0)

    def shrink_border(self, factor):
        self.top_left = self.add_cord(self.top_left, number=factor)
        self.top_right = self.add_cord(self.top_right, cord_tuple2=(-factor, factor))
        self.bottom_left = self.add_cord(
            self.bottom_left, cord_tuple2=(factor, -factor)
        )
        self.bottom_right = self.add_cord(
            self.bottom_right, cord_tuple2=(-factor, -factor)
        )

    def draw(self, surface):
        rects = [
            self.rect_from_2_points((0, 0), (self.top_right[0], self.top_left[1])),
            self.rect_from_2_points(DISPLAY_SIZE, (0, self.bottom_left[1])),
            self.rect_from_2_points((0, self.top_left[1]), self.bottom_left),
            self.rect_from_2_points((DISPLAY_SIZE[0], 0), self.bottom_right),
        ]
        for rect in rects:
            pygame.draw.rect(surface, self.color, rect)

    @staticmethod
    def add_cord(cord_tuple, *, number=0, cord_tuple2=(0, 0)):
        return (
            cord_tuple[0] + number + cord_tuple2[0],
            cord_tuple[1] + number + cord_tuple2[1],
        )

    @staticmethod
    def rect_from_2_points(pt1, pt2):
        rect = pygame.Rect(*pt1, pt2[0] - pt1[0], pt2[1] - pt1[1])
        rect.normalize()
        return rect


class Player:
    direction = RIGHT
    rotation = 0
    length = 1
    previous_length = 1
    init_length = 1
    max_length = 2
    length_step = 1
    movment_speed = 1
    size = 1
    last_size = 1
    size_step = 1
    SNAKE_BODY_IMAGE = None
    snake_body_image = None
    SNAKE_HEAD_IMAGE = None
    snake_head_image = None

    def __init__(
        self,
        *,
        starting_length,
        starting_size,
        size_step,
        max_length,
        length_step,
        movment_speed,
        border,
    ):
        self.validate_length(starting_length, max_length)
        # length of the snake
        self.length = self.init_length = self.previous_length = starting_length
        # when snake's length is greater than max_length
        # it will be reset to init_length and size will be increased
        self.max_length, self.length_step = max_length, length_step
        self.size = self.last_size = starting_size
        self.size_step = size_step
        self.movment_speed = movment_speed

        self.x = collections.deque([self.movment_speed] * self.init_length)
        self.y = collections.deque([self.movment_speed] * self.init_length)

        self.SNAKE_BODY_IMAGE = pygame.image.load("Assets/Textures/snake-body.png")
        self.snake_body_image = self.SNAKE_BODY_IMAGE
        self.SNAKE_HEAD_IMAGE = pygame.image.load("Assets/Textures/snake-head.png")
        self.snake_head_image = self.SNAKE_HEAD_IMAGE
        self.border = border
        self.animation = GrowingAnimation(self, self.border)

    @staticmethod
    def validate_length(starting_length, max_length):
        if max_length <= starting_length:
            raise ValueError("max_length must be greater than starting_length")

    def rotate_snake_texture(
        self,
        degrees,
        *,
        default_body_image=None,
        default_head_image=None,
    ):

        if default_body_image is None:
            default_body_image = self.SNAKE_BODY_IMAGE
        if default_head_image is None:
            default_head_image = self.SNAKE_HEAD_IMAGE

        self.rotation = degrees
        if degrees == 0:
            self.snake_body_image = default_body_image
            self.snake_head_image = default_head_image
            return

        self.snake_body_image = pygame.transform.rotate(default_body_image, degrees)
        self.snake_head_image = pygame.transform.rotate(default_head_image, degrees)

    def update(self):
        if self.length >= self.max_length:
            self.length = self.previous_length = self.previous_length
            self.size += self.size_step
            self.x = collections.deque(itertools.islice(self.x, 0, self.length))
            self.y = collections.deque(itertools.islice(self.y, 0, self.length))
        if self.previous_length == self.length:
            self.x.pop()
            self.y.pop()
        else:
            self.previousLength = self.length

        movement = (
            self.direction[0] * self.movment_speed,
            self.direction[1] * self.movment_speed,
        )

        # head position handling
        self.x.appendleft(self.x[0] + movement[0])
        self.y.appendleft(self.y[0] + movement[1])

    def move(self, direction):
        if direction not in (UP, DOWN, LEFT, RIGHT):
            raise ValueError(
                f"invalid direction, must be 'UP', 'DOWN', 'LEFT' or 'RIGHT' while got {direction}"
            )

        # if snake is moving in opposite direction
        if direction[0] * self.direction[0] < 0 or direction[1] * self.direction[1] < 0:
            return False
        self.direction = direction
        return True

    def draw(self, surface, *, body_image, head_image):
        for i in range(1, self.length):
            surface.blit(body_image, (self.x[i], self.y[i]))
        surface.blit(head_image, (self.x[0], self.y[0]))


class Game:
    def __init__(self):
        # initialising music and text
        self.background_music = pygame.mixer.Sound("Assets/Music/background-music.ogg")
        self.eat_sound = pygame.mixer.Sound("Assets/SFX/eat-sound.wav")
        self.grow_sound = pygame.mixer.Sound("Assets/SFX/grow-sound.wav")

    def test_collision(self, x1, y1, x2, y2):
        return x1 == x2 and y1 == y2


class App:
    fps = 10

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.game = Game()

        self.border = Border()
        snake_movement_speed = 20
        self.player = Player(
            starting_length=3,
            starting_size=1,
            max_length=10,
            size_step=1,
            length_step=1,
            movment_speed=snake_movement_speed,
            border=self.border,
        )

        self._screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
        self._display_surf = pygame.Surface(DISPLAY_SIZE)

        pygame.display.set_caption("It Grows!")

        self.player.SNAKE_BODY_IMAGE = pygame.image.load(
            "Assets/Textures/snake-body.png"
        )
        self.player.snake_body_image = self.player.SNAKE_BODY_IMAGE
        self.player.SNAKE_HEAD_IMAGE = pygame.image.load(
            "Assets/Textures/snake-head.png"
        )
        self.player.snake_head_image = self.player.SNAKE_HEAD_IMAGE
        self.food_images = [
            pygame.image.load("Assets/Textures/small-food.png"),
            pygame.image.load("Assets/Textures/medium-food.png"),
        ]
        self.food_images_sizes = [
            (8, 8),
            (16, 16),
        ]

        # create food {len(food_images)} times
        self.food = [
            Food(
                *self.calculate_food_position(
                    self.border.top_left, self.border.bottom_right
                ),
                texture_size=size,
            )
            for _, size in zip(self.food_images, self.food_images_sizes)
        ]

    def game_over(self):
        pygame.quit()
        quit()

    def draw(self):
        self._display_surf.fill((255, 255, 255))
        for food, food_image in zip(self.food, self.food_images):
            food.draw(self._display_surf, food_image)
        self.player.draw(
            self._display_surf,
            body_image=self.player.snake_body_image,
            head_image=self.player.snake_head_image,
        )
        self.border.draw(self._display_surf)
        self._screen.blit(
            pygame.transform.scale(self._display_surf, WINDOW_SIZE), (0, 0)
        )
        pygame.display.update()

    def calculate_food_position(self, pt1, pt2):
        return (
            random.randint(
                (pt1[0] // self.player.movment_speed) - 1,
                (pt2[0] // self.player.movment_speed) - 1,
            )
            * self.player.movment_speed
        ), (
            random.randint(
                (pt1[1] // self.player.movment_speed) - 1,
                (pt2[1] // self.player.movment_speed) - 1,
            )
            * self.player.movment_speed
        )

    def tick(self):
        self.draw()
        clock.tick(self.fps)
        print(clock.get_fps())

    def run(self):
        self.player.rotate_snake_texture(-90)
        pygame.mixer.Channel(0).play(self.game.background_music, loops=-1)
        pygame.mixer.Channel(0).set_volume(0.01)
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.game_over()
                elif event.type == KEYDOWN:
                    if event.key == K_RIGHT and self.player.move(RIGHT):
                        self.player.rotate_snake_texture(-90)
                    elif event.key == K_LEFT and self.player.move(LEFT):
                        self.player.rotate_snake_texture(90)
                    elif event.key == K_UP and self.player.move(UP):
                        self.player.rotate_snake_texture(0)
                    elif event.key == K_DOWN and self.player.move(DOWN):
                        self.player.rotate_snake_texture(180)
                    else:
                        continue
                    break
            # jump to next game tick skipping all the game logic if the animation returned True
            if self.player.animation.play():
                self.tick()
                continue
            # test if eating food 🍔
            for food in self.food:
                collided = self.game.test_collision(
                    self.player.x[0], self.player.y[0], food.x, food.y
                )
                if collided:
                    pygame.mixer.Channel(1).play(self.game.eat_sound)
                    pygame.mixer.Channel(1).set_volume(0.01)
                    food.x, food.y = self.calculate_food_position(
                        self.border.top_left, self.border.bottom_right
                    )

                    self.player.length += self.player.length_step

            self.player.update()

            # if hits the wall
            if (
                self.player.x[0] < 0
                or self.player.x[0] > DISPLAY_SIZE[0] - self.player.movment_speed
                or self.player.y[0] < 0
                or self.player.y[0] > DISPLAY_SIZE[1] - self.player.movment_speed
            ):
                self.game_over()

            # check to see if snake collides with itself
            for i in range(2, self.player.length - 1):
                if self.game.test_collision(
                    self.player.x[0],
                    self.player.y[0],
                    self.player.x[i],
                    self.player.y[i],
                ):
                    self.game_over()

            if self.player.size > self.player.last_size:
                self.player.last_size = self.player.size
                self.player.snake_body_image = pygame.transform.rotate(
                    self.player.SNAKE_BODY_IMAGE, -90
                )
                self.player.snake_head_image = pygame.transform.rotate(
                    self.player.SNAKE_HEAD_IMAGE, -90
                )

                # we scale the food size down which will make the illusion of getting bigger
                food_images_copy = self.food_images.copy()
                food_copy = self.food.copy()
                deleted_count = 0
                for enum_food_images, food in zip(
                    enumerate(food_images_copy), food_copy
                ):
                    i, food_image = enum_food_images
                    i -= deleted_count
                    food_image_size = food_image.get_size()
                    self.food_images[i] = pygame.transform.scale(
                        food_image,
                        (
                            food_image_size[0] // self.player.size,
                            food_image_size[1] // self.player.size,
                        ),
                    )
                    food.texture_size = (
                        food.texture_size[0] // self.player.size,
                        food.texture_size[1] // self.player.size,
                    )

                    if food.texture_size[0] < 2 or food.texture_size[1] < 2:
                        self.food_images.pop(i)
                        self.food.pop(i)
                        deleted_count += 1
                        continue

                pygame.mixer.Channel(1).play(self.game.grow_sound)
                self.player.animation.playing = True
            self.tick()


if __name__ == "__main__":
    App().run()
