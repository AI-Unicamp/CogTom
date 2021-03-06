# Eye-Direction Detector
# EDD basic functions are:
#   detects the presence of eyes/eyes-like stimuli
#   computes whether eyes are directed towards agents/objects
#   infers agents knowledge attributing perceptual states.
import numpy as np
from output.logger import Logger
from model.model import Model
import pandas as pd

class Edd(Model):

    def __init__(self, max_steps):
        Model.__init__(self, Logger.MODEL_EDD, max_steps)

    def set(self, entities_arr, agents):
        self.edd_entities = entities_arr
        # Assume that all agents have eyes.
        self.edd_eyes = np.array(agents)

    def process(self, eye_dir_arr):
        # Dimensions for the EDD Eye Direction Array are (agent) lines
        # and (entities) columns.
        lines = self.edd_eyes.shape[0]
        cols = self.edd_entities.shape[0] 

        self.edd_eye_dir = np.zeros((lines, cols), dtype=int)
        for entry in range(eye_dir_arr.shape[0]):
            # For each line in the visual system, identify the object 
            # and fill in the EDD eye direction array.
            # By convention the array is configured as:
            #         Agent1 Obj1 Obj2 Obj3
            # Agent1     0    0/1  0/1  0/1
            # Agent2     0    0/1  0/1  0/1
            # where 0 is no gaze and 1 is a gaze.
            agent = eye_dir_arr[entry, 0]
            obj = eye_dir_arr[entry, 1]
            # identify row for insertion
            l = np.where(self.edd_eyes == agent)[0]
            c =  np.where(self.edd_entities == obj)[0]
            # Set as '1' to identify a object that is in the visual field of the agent.
            self.edd_eye_dir[l, c] = 1

        # Now create the EDD Agent store
        # For each agent list the entities in its visual space
        self.edd_agent_store = np.array([])
        ag_store_lst = []
        for agent in range(self.edd_eyes.shape[0]):
            # For each agent line in edd_eyes
            ag_list = []
            for eye_dir in range(self.edd_eye_dir.shape[1]):
                if self.edd_eye_dir[agent, eye_dir] == 1:
                    # Add to agent store
                    ag_list.append(self.edd_entities[eye_dir,0])
            ag_store_lst.append(ag_list)
        self.edd_agent_store = np.array(ag_store_lst)
        
        # Create EDD Gaze Register
        # The Gaze Register identifies agents that are looking at each other.
        mg_lst = []
        for ag in range(self.edd_eyes.shape[0]):
            # For each agent line in edd_eyes
            agent1 = self.edd_eyes[ag]
            for eye_dir in range(self.edd_eye_dir.shape[1]):
                if self.edd_eye_dir[ag, eye_dir] == 1:
                    # Check if entity being looked at is an agent, too.
                    entity = self.edd_entities[eye_dir,0]
                    is_agent = self.edd_entities[eye_dir,1]
                    if (is_agent):
                        # It is an agent too, so check if it is also looking back at the first agent. 
                        # To do that, we search on the EDD eye direction matrix.
                        l = np.where(self.edd_eyes == entity)[0]
                        c = np.where(self.edd_entities == agent1)[0]
                        if self.edd_eye_dir[l,c] == 1:
                            # Mutual Gaze confirmed, add to list.
                            mg_tuple = (agent1, entity)
                            # Is it in the list, already? Check for duplicates.
                            mg_tuple_inv = mg_tuple[::-1]
                            if (mg_tuple not in mg_lst) and (mg_tuple_inv not in mg_lst):
                                mg_lst.append(mg_tuple)
        # Add list to np array.
        self.edd_gaze_register = np.array(mg_lst)
    
    def print(self, t):
        msg = "Evaluating Mind Step " + str(t)
        self.logger.write(msg, t)
        self.logger.write("EDD:", t)
        self.logger.write("Entities: " + str(self.edd_entities[:,0]), t)
        self.logger.write("Eye_Direction: " + str(self.edd_eye_dir), t)
        self.logger.write("Agent_Store: " + str(self.edd_agent_store), t)
        self.logger.write("Gaze_Register:" + str(self.edd_gaze_register), t)

         # Latex
        df_ent = pd.DataFrame(self.edd_entities[:,0], columns=['Entities'])
        if not df_ent.empty:
            self.logger.write_tex(df_ent.to_latex(index=False, caption='EDD Entities Table'), t)
        df_eye = pd.DataFrame(self.edd_eye_dir, columns = self.edd_entities[:,0])
        if not df_eye.empty:
            df_eye = df_eye.set_index(pd.Index(self.edd_eyes))
            self.logger.write_tex(df_eye.to_latex(index=True, caption='EDD Eye Direction Table'), t)
        df_agt = pd.DataFrame(self.edd_agent_store)
        if not df_agt.empty:
            df_agt = df_agt.set_index(pd.Index(self.edd_eyes))
            self.logger.write_tex(df_agt.to_latex(index=True, caption='EDD Agent Store'), t)
        df_gaze = pd.DataFrame(self.edd_gaze_register)
        if not df_gaze.empty:
            self.logger.write_tex(df_gaze.to_latex(index=False, caption='EDD Gaze Register'), t)







        

        


