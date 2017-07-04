import gym
from gym import spaces
from obstacles import Robot, Obstacle
import numpy as np
import random
from gym.envs.classic_control import rendering
import time

STILL, LEFT, RIGHT = 0, 1, 2


class RobotEnv(gym.Env):
    metadata = {'render.modes': ['human'], 'video.frames_per_second': 1}

    def __init__(self):
        self.width = 600
        self.height = 600
        self.robot_width = 50
        self.robot_height = 30
        self.obstacles = []
        wall_size = 5
        self.robot = Robot([self.width / 2, self.height / 2],
                           self.robot_width, self.robot_height)
        self.obstacle = Obstacle([500, 300], 50, 50)
        leftWall  = Obstacle([0,self.height/2],wall_size,self.height)
        rightWall = Obstacle([self.width,self.height/2],wall_size,self.height)
        topWall = Obstacle([self.width/2,self.height],self.width,wall_size)
        botWall = Obstacle([self.width/2,0],self.width,wall_size)
        self.obstacles = [self.obstacle,leftWall,rightWall,topWall,botWall]
        self.walls = [leftWall,rightWall,topWall,botWall]
        self.speed = 0.5
        self.pad_width = 1
        self.action_space = spaces.Discrete(4)  # Left, Right, Foward
        self.observation_space = spaces.Box(
            low=0, high=600, shape=(self.height, self.width))

        self.viewer = None
        self.state = None

        self._reset()
        self._configure()

    def _configure(self, display=None):
        self.display = display

    def _step(self, action):
        assert self.action_space.contains(
            action), "%r (%s) invalid" % (action, type(action))
        
        if(action == 0):
            self.robot.move_forward()
            pass
        if(action == 1):
            self.robot.turn_left()
        if(action == 2):
            self.robot.turn_right()   
        reward, done = self.reward()
        return np.copy(self.state), reward, done, {}

    def reward(self):
        pos = self.robot.get_postion()
        for obs in self.obstacles:         
            if self.robot.collision(obs):
                return -100, True
        return 0, False

    def _reset(self):
        self.state = np.zeros(5,)
        # x
        self.robot = Robot([self.width / 2, self.height / 2],
                           self.robot_width, self.robot_height)
        return np.copy(self.state)

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        if self.viewer is None:
            self.viewer = rendering.Viewer(
                self.width, self.height, display=self.display)

            robot = rendering.FilledPolygon(self.robot.get_drawing())
            cast = rendering.make_circle(2,)
            start = rendering.make_circle(3)
            obs = rendering.FilledPolygon(self.obstacle.get_drawing())
            for wall in self.walls:
                draw = rendering.FilledPolygon(wall.get_drawing_static_position())
                #draw.set_color(0,0,1)
                self.viewer.add_geom(draw)
            self.obtrans = rendering.Transform()
            self.casttrans = rendering.Transform()
            self.starttrans = rendering.Transform()
            self.robottrans = rendering.Transform()
            robot.add_attr(self.robottrans)
            obs.add_attr(self.obtrans)
            cast.add_attr(self.casttrans)
            start.add_attr(self.starttrans)
            cast.set_color(1,0,0)
            start.set_color(1,0,0)
            self.viewer.add_geom(robot)
            self.viewer.add_geom(start)
            self.viewer.add_geom(obs)
            self.viewer.add_geom(cast)
            
        if self.state is None:
            return None

        min, points, pos = self.robot.getUltraSonicSensorData(self.obstacles)
        print(min)
        x, y = self.obstacle.get_postion()[0], self.obstacle.get_postion()[1]
        self.obtrans.set_translation(x, y)
        x = self.robot.get_postion()[0]
        y = self.robot.get_postion()[1]
        rot = self.robot.get_rotation()
        self.starttrans.set_translation(pos[0],pos[1])
        self.casttrans.set_translation(points[0],points[1])
        
        self.robottrans.set_translation(x, y)
        self.robottrans.set_rotation(rot * np.pi / 180)
        return self.viewer.render()
    
    def create_environment(self):
        robot = rendering.FilledPolygon(self.robot.get_drawing())
        cast = rendering.make_circle(2,)
        start = rendering.make_circle(3)
        obs = rendering.FilledPolygon(self.obstacle.get_drawing())
        self.obtrans = rendering.Transform()
        self.casttrans = rendering.Transform()
        self.starttrans = rendering.Transform()
        self.robottrans = rendering.Transform()