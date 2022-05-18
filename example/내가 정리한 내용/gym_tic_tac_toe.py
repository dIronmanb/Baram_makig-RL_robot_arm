import gym

class TicTacToeEnv(gym.Env):
    
    metadata = {'render.modes': ['human']} # rendering mode
    
    
    def step(self, action):
        
        # position the mark to the position of the given action
        loc = action
        reward = NO_REWARD
        self.board[loc] = tocode(self.mark)
        
        # Return rewards that match the mark when a win/loss is determined
        status = check_game_status(self.board)
        if status >= 0:
            self.done = True
            if status in [1,2]:
                reward = O_REWARD if self.mark == 'O' else X_REWARD
                
        # change the other player
        self.mark = next_mark(self.mark)
        
        return self._get_obs(), reward, self.done, None
         
    
    def reset(self):
        # initialize environment
        
        self.board = [0] * 9
        self.mark  = 'O'
        self.done = False
        
        # GET observation
        return self._get_obs()
    
    def _get_obs(self):
        # observation: state or board + next mark
        return tuple(self.board), self.mark
     
    
    def render(self, mode = 'human', close = False):
        
        # Mark up board only when human mode
        if mode =='human':
            self._show_board(print)
        
    def _show_board(self, showfn):
        # draw board
        for j in range(0, 9, 3):
            
            # Change mark code into character: 0 >> ' ' / 1 >> 'O' / 2 >> 'X'
            print('|'.join([tomark(self.board[i]) for i in range(j, j + 3)]))
            if j < 6:
                print('---------')
                
                
    def play(show_number):
        env = TicTacToeEnv(show_number = show_number)
        agents = [HumanAgent('O'),
                  HumanAgent('X')]
        
        episode = 0
        
        while True:
            state = env.reset()
            _ , mark = state            
            done = False
            env.render()
            while not done:
                agent = agent_by_mark(agents, next_mark(mark))
                env.show_trun(True, mark)
                ava_actions = env.available_actions()
                action = agent.act(ava_actions)
                if action is None:
                    sys.exit()
                    
                    
                state. reward, done, info = env.step(action)
                
                print('')
                env.render()
                if done:
                    env.show_result(True, mark, reward)
                    break
                else:
                    _, mark = state
                    
            episode += 1
            
            
            
            
            
            
            