# Jordan Makansi
# 01/19/19

import numerical_propagator as prp

import unittest   
import numpy as np 
import abc
import scipy as sp
import ode

from blackboard import *

class AgentChecker:
    '''
    This class is used to check the properties of agents:
      - it makes sure the dimensions are consistent for all of the methods
      - it makes sure the outputs of each method are consistent
    ''' 
    def __init__(self, agent): 
        '''
        Inputs: 
            agent: instance of class Agent.  
        Outputs(None):
        '''

    def checkAll(self, agent):
        '''
        Inputs:
        '''
        # Inputs for numerical integration
        self.integrateTol = integrateTol
        self.integrateMaxIter = integrateMaxIter

        # Inputs for sliding window
        self.t_0 = t_0 
        self.T = T 
        self.K = K

        self.t_terminal = t_terminal # terminate entire simulation of this agent
        self.n_s = n_s # number of steps inside of each bucket

        # data
        self.q_1_0 = kwargs['q_1_0']
        self.q_B_0 = kwargs['q_B_0']
        self.v_c_u_0 = kwargs['v_c_u_0']
        self.v_c_1_0 = kwargs['v_c_1_0']

        # Parameters
        self.c_1 = kwargs['c_1']
        self.R_0 = kwargs['R_0']
        self.R_1 = kwargs['R_1']
        self.v_a = kwargs['v_a']
        self.Q_0 = kwargs['Q_0']
        self.beta = kwargs['beta']
        self.v_N = kwargs['v_N']

        self.validate_dimensions()


    def validate_dimensions(self):
        # TODO: move to parent class "SlidingWindow"
        assert len(self.state_indices) == self.state_dim, 'state dimensions are not consistent.  dimension of state indices is '+str(len(self.state_indices)) +' and state_dim is '+str(self.state_dim)
        assert len(self.control_indices) == len(self.u_s_0), 'control dimensions are not consistent.  dimension of control_indices is '+str(len(self.control_indices)) +' and len(u_0) is '+str(len(self.u_s_0))
        assert len(self.qpu_vec) == 3*self.state_dim + len(self.control_indices), ' control and state dimensions are not consistent with qpu_vec : length of qpu_vec is '+str(len(self.qpu_vec))+ ' and 3*self.state_dim + len(self.control_indices) is ' + str(3*self.state_dim + len(self.control_indices))
    
 
    # local methods
    #def L_l(self, q_1, q_B, q_1_dot, q_B_dot, u_B, q_1_0, q_B_0, v_c_u_0, v_c_1_0, c_1, R_0, R_1, v_a, Q_0, beta, v_N):
    # TODO: Change notation to be consistent with Steve's document:  e.g. instead of q_B, use qb
    def L_l(self, q_s, q_s_dot, u_s):
        '''
        Inputs:
            states:
                q_1: charge 1 at time t
                q_B: charge of battery at time t
            control:
                u_B: control of battery
            data:
                q_1_0:
                q_B_0:
                v_c_u_0:
                v_c_1_0:
            parameters:
                c_1:
                R_0:
                R_1:
                v_a:
                Q_0:
                beta:
                v_N:
        '''
        # Immediately extract q_s, q_s_dot, and u_s out of it
        q_1 = q_s[0]
        q_B = q_s[1]

        q_1_dot = q_s_dot[0]
        q_B_dot = q_s_dot[1]

        u_B = u_s

        # TODO: replace as a function of self.K and self.T
        delta = 1
        # q_1_0, q_B_0, v_c_u_0, v_c_1_0, c_1, R_0, R_1, v_a, Q_0, beta, v_N = kwargs['q_1_0'], kwargs['q_B_0'], kwargs['v_c_u_0'], kwargs['v_c_1_0'],kwargs['c_1'], kwargs['R_0'], kwargs['R_1'], kwargs['v_a'], kwargs['Q_0'], kwargs['beta'],kwargs['v_N']

        # data
        q_1_0 = self.q_1_0
        q_B_0 = self.q_B_0
        v_c_u_0 = self.v_c_u_0
        v_c_1_0 = self.v_c_1_0

        # Parameters
        c_1 = self.c_1
        R_0 = self.R_0
        R_1 = self.R_1
        v_a = self.v_a
        Q_0 = self.Q_0
        beta = self.beta
        v_N = self.v_N

        V_c_1 = (c_1/2.0)*((((q_1 - q_1_0)/c_1) + v_c_1_0)**2 - v_c_1_0)
        V_c_u = 0.5*(u_B*(-(q_B - q_B_0))**2+2*(-(q_B - q_B_0)*v_c_u_0))
        D_R_0 = 0.5*(-q_B_dot**2)*R_0*delta  
        D_R_1 = 0.5*((-q_B_dot - q_1_dot)**2)*R_1*delta
        F_B = -(v_N/beta**2)*(beta*q_B - beta*q_B_0 + (Q_0*beta - Q_0)*np.log( (Q_0 - Q_0*beta + beta*q_B) / (Q_0 - Q_0*beta + beta*q_B_0)))
        F_B_out = -(q_B - q_B_0)*v_a

        L_l = -V_c_1 - V_c_u + D_R_0 + D_R_1 + F_B - F_B_out
        return  L_l

    def L_l_q_dot(self, q_s, q_s_dot, u_s):
        '''
        '''
        # TODO: replace as a function of self.K and self.T
        delta = 1
        q_1 = q_s[0]
        q_B = q_s[1]

        q_1_dot = q_s_dot[0]
        q_B_dot = q_s_dot[1]

        u_B = u_s
        p_1 = (q_B_dot+q_1_dot)*self.R_1*delta
        p_B = q_B_dot*(self.R_0+self.R_1)*delta + q_1_dot*self.R_1*delta
        return np.array([p_1, p_B])

    def L_mf_q_dot(self, q_mf, q_mf_dot, u_mf):
        # q_mf_dot, q_mf (inputs) here will be vectors with ALL of the states
        # u_mf is a vector of ALL of the controls
        # extract q_s from q_mf
        
        # note that these methods must return vectors that are of local dimension - state_dim - even though they take in vectors of dimension for all the states
        # the user needs to be aware of the indices the correspond to each state
        # TODO: replace as a function of self.K and self.T
        delta = 1

        # TODO: replace with actual L_l_q_dot for each agent.  currently these are fake.        
        def L_l_q_dot_building1(q_mf, q_mf_dot, u_mf):
            return np.array(q_mf[0])
        
        def L_l_q_dot_building2(q_mf, q_mf_dot, u_mf):
            return np.array(q_mf[1])
        
        L_mf_total_q_dot = np.zeros(self.state_dim)

        # agent 1
        L_mf_total_q_dot += L_l_q_dot_building1(q_mf, q_mf_dot, u_mf)

        # agent 2
        L_mf_total_q_dot += L_l_q_dot_building2(q_mf, q_mf_dot, u_mf)
        assert np.shape(L_mf_total_q_dot)[0] == self.state_dim, 'dimensions of L_mf_total_q_dot must match those of the local state, currently the dimensions are ' +str(np.shape(L_mf_total_q_dot)[0])
        return L_mf_total_q_dot


    def H_l(self, q_s, p_l, u_s, lambda_l):
        # call using q_s, p_l, lambda_l
        H_l_nou = self.H_l_nou(q_s, p_l, lambda_l) 
        H_l_u = self.H_l_u(q_s, p_l)
        H_l = H_l_nou + np.dot(H_l_u, u_s)
        return H_l

    def H_l_nou(self, q_s, p_l, lambda_l):
        # TODO: replace as a function of self.K and self.T
        delta = 1
        q_1, q_B = q_s[0], q_s[1]
        p_1, p_B = p_l[0], p_l[1]
        # data
        q_1_0 = self.q_1_0
        q_B_0 = self.q_B_0
        v_c_u_0 = self.v_c_u_0
        v_c_1_0 = self.v_c_1_0

        # Parameters
        c_1 = self.c_1
        R_0 = self.R_0
        R_1 = self.R_1
        v_a = self.v_a
        Q_0 = self.Q_0
        beta = self.beta
        v_N = self.v_N

        term_1 = 0.5*(((p_B-p_1)**2)/(R_0 * delta)) + 0.5*((p_1**2)/(R_1*delta))
        term_2 = (c_1/2)*((((q_1-q_1_0)/c_1) + v_c_1_0)**2 - v_c_1_0**2) 
        term_3 = (-(q_B - q_B_0)*v_c_u_0) 
        term_4 =  (v_N/beta)*(beta*q_B - beta*q_B_0 +(Q_0*beta - Q_0)*np.log( (Q_0 - Q_0*beta + beta*q_B) / (Q_0 - Q_0*beta + beta*q_B_0)))
        term_5 = -(q_B-q_B_0)*v_a
        return term_1 + term_2 + term_3 + term_4 + term_5

    def H_l_u(self, q_s, p_l):
        # this returns a 1D numpy array, of dimension control_dim  
        q_1, q_B = q_s[0], q_s[1]
        q_B_0 = self.q_B_0
        term_1 = 0.5*(-(q_B - q_B_0))**2 
        return np.array([term_1])

    def q_rhs_H_l_nou(self, q_s, p_l, lambda_l):
        # TODO: replace as a function of self.K and self.T
        delta = 1
        q_1, q_B = q_s[0], q_s[1]
        p_1, p_B = p_l[0], p_l[1]
 
        # data
        q_1_0 = self.q_1_0
        q_B_0 = self.q_B_0
        v_c_u_0 = self.v_c_u_0
        v_c_1_0 = self.v_c_1_0

        # Parameters
        c_1 = self.c_1
        R_0 = self.R_0
        R_1 = self.R_1
        v_a = self.v_a
        Q_0 = self.Q_0
        beta = self.beta
        v_N = self.v_N


        q_1_rhs_H_l_nou = (q_1 - q_1_0)/c_1 + v_c_1_0
        q_B_rhs_H_l_nou = -v_c_u_0 - v_a + (v_N/beta) + (v_N*Q_0*(beta-1))/(beta*(Q_0 - Q_0*beta + beta*q_B))
        q_rhs_H_l_nou = np.concatenate([np.array([q_1_rhs_H_l_nou]), np.array([q_B_rhs_H_l_nou])])
        return q_rhs_H_l_nou

    def p_rhs_H_l_nou(self, q_s, p_l, lambda_l):
        # TODO: replace as a function of self.K and self.T
        delta = 1
        q_1, q_B = q_s[0], q_s[1]
        p_1, p_B = p_l[0], p_l[1]
 
        # data
        q_1_0 = self.q_1_0
        q_B_0 = self.q_B_0
        v_c_u_0 = self.v_c_u_0
        v_c_1_0 = self.v_c_1_0

        # Parameters
        c_1 = self.c_1
        R_0 = self.R_0
        R_1 = self.R_1
        v_a = self.v_a
        Q_0 = self.Q_0
        beta = self.beta
        v_N = self.v_N

        p_1_rhs_H_l_nou = -p_B/(R_0*delta) + (p_1/delta)*((1/R_0)+(1/R_1))
        p_B_rhs_H_l_nou = (p_B - p_1)/(R_0*delta)
        p_rhs_H_l_nou = np.concatenate([np.array([p_1_rhs_H_l_nou]), np.array([p_B_rhs_H_l_nou])])
        return p_rhs_H_l_nou

    def q_rhs_H_l_u(self, q_s, p_l):
        # TODO: replace as a function of self.K and self.T
        delta = 1
        q_1, q_B = q_s[0], q_s[1]
 
        # data
        q_B_0 = self.q_B_0

        q_1_rhs_H_l_u = 0
        q_B_rhs_H_l_u = q_B - q_B_0
        q_rhs_H_l_u = np.concatenate([np.array([q_1_rhs_H_l_u]), np.array([q_B_rhs_H_l_u])])
        return np.array([q_rhs_H_l_u])

    def p_rhs_H_l_u(self, q_s, p_l):
        # TODO: replace as a function of self.K and self.T
        delta = 1
        p_1_rhs_H_l_u = 0
        p_B_rhs_H_l_u = 0
        p_rhs_H_l_u = np.concatenate([np.array([p_1_rhs_H_l_u]), np.array([p_B_rhs_H_l_u])])
        return np.array([p_rhs_H_l_u])

    def q_rhs_H_l(self, q_s, p_l, u_s, lambda_l):
        q_rhs_H_l = self.q_rhs_H_l_nou(q_s, p_l, lambda_l) + np.dot(self.q_rhs_H_l_u(q_s, p_l).T, u_s)
        # should return something of dimension state_dim 
        return q_rhs_H_l

    def p_rhs_H_l(self, q_s, p_l, u_s, lambda_l):
        p_rhs_H_l = self.p_rhs_H_l_nou(q_s, p_l, lambda_l) + np.dot(self.p_rhs_H_l_u(q_s, p_l).T, u_s)
        # should return something of dimension state_dim 
        return p_rhs_H_l

    def qp_rhs_H_l(self, q_s, p_l, u_s, lambda_l):
        q_rhs_H_l = self.q_rhs_H_l(q_s, p_l, u_s, lambda_l)
        p_rhs_H_l = self.p_rhs_H_l(q_s, p_l, u_s, lambda_l)
        return np.concatenate([q_rhs_H_l, p_rhs_H_l])

    # Mean Field methods
    def H_mf_nou(self, q_mf, p_mf, u_mf):
        # should return a scalar
        return 1

    def H_mf_u(self, q_mf, p_mf, u_mf):
        # should return a 1D numpy array of dimension control_dim
        return np.array([1])

    def q_rhs_H_mf_u(self, q_mf, p_mf, u_mf):
        # should return 2D numpy array of dimension control_dim x state_dim
        # Normally, we would wrap this in a numpy array like np.array([p_H_mf_u_dot_1]), but since we are stealing from local in this case it is not necessary
        return np.ones((1, 2))

    def p_rhs_H_mf_u(self, q_mf, p_mf, u_mf):
        # should return 2D numpy array of dimension control_dim x state_dim
        # TODO: Change to actual mean field.  For now just use local functions.
        return np.ones((1, 2))

    def q_rhs_H_mf_nou(self, q_mf, p_mf):
        # should return 1D numpy array of dimension state_dim
        q_1  = q_mf[0]
        q_B  = q_mf[1]
        qfb1  = q_mf[2]
        qab1  = q_mf[3]
        qwb1  = q_mf[4]
        phil1b1  = q_mf[5]
        qfb2  = q_mf[6]
        qab2  = q_mf[7]
        qwb2  = q_mf[8]
        phil1b2  = q_mf[9]
         
        return np.zeros((self.state_dim))

    def p_rhs_H_mf_nou(self, q_mf, p_mf):
        # should return 1D numpy array of dimension state_dim
        # TODO: Change to actual mean field.  For now just use local functions.
        return np.zeros((self.state_dim))

    def p_rhs_H_mf(self, q_mf, p_mf, u_mf, u_s):
        # q_rhs_H_mf is the derivative wrt each of the local variables, so it will return something of dimension state_dim # q_rhs_H_mf_u returns the partial derivatives wrt each control, concatenated together
        p_rhs_H_mf_u = self.p_rhs_H_mf_u(q_mf, p_mf, u_mf)
        assert np.shape(p_rhs_H_mf_u)==(len(self.control_indices), self.state_dim) # first dimension should be number of controls, inner dimension should be state_dim
        # since only one control, no need for dot product here
        p_rhs_H_mf_u_summed = np.dot(self.p_rhs_H_mf_u(q_mf, p_mf, u_mf).T, u_s)        
        return self.p_rhs_H_mf_nou(q_mf, p_mf) + p_rhs_H_mf_u_summed

    def q_rhs_H_mf(self, q_mf, p_mf, u_mf, u_s):
        # q_rhs_H_mf is the derivative wrt each of the local variables, so it will return something of dimension state_dim # q_rhs_H_mf_u returns the partial derivatives wrt each control, concatenated together
        q_rhs_H_mf_u = self.q_rhs_H_mf_u(q_mf, p_mf, u_mf)
        assert np.shape(q_rhs_H_mf_u)==(len(self.control_indices), self.state_dim) # first dimension should be number of controls, inner dimension should be state_dim
        q_rhs_H_mf_u_summed = np.dot(self.q_rhs_H_mf_u(q_mf, p_mf, u_mf).T, u_s)        
        # ---- How do we get this in terms of q_mf, p_mf, and u_mf ?
        return self.q_rhs_H_mf_nou(q_mf, p_mf) + q_rhs_H_mf_u_summed

    def qp_rhs_H_mf(self, q_mf, p_mf, u_mf, u_s):
        # remember that we want to propagate as much as possible together in the same rhs function for numerical purposes
        # remember that q_rhs here is w.r.t p_mf but p_rhs here is w.r.t q_s
        q_H_mf_dot = self.p_rhs_H_mf(q_mf, p_mf, u_mf, u_s)
        p_H_mf_dot = self.q_rhs_H_mf(q_mf, p_mf, u_mf, u_s)
        return np.concatenate([q_H_mf_dot, p_H_mf_dot])

    def qp_rhs(self, t, qp_vec, **kwargs):
        '''
        '''
        # This is what the input is going to look like:  0.0, qp_vec, state_dim=sliding_window_instance.state_dim, Gamma = sliding_window_instance.Gamma, u_0 = u_0, q_mf=q_mf, u_mf=u_mf)
        state_dim = self.state_dim

        q_s = qp_vec[:state_dim]
        q_1, q_B = q_s[0], q_s[1]

        p_l = qp_vec[state_dim:2*state_dim]
        p_mf = qp_vec[2*state_dim:]

        p_1, p_B = p_l[0], p_l[1]

        u_s = kwargs['u_0']
        q_mf = kwargs['q_mf']
        u_mf = kwargs['u_mf']
        lambda_l = kwargs['lambda_l']

        # see if this works because I think only qp_rhs is external facing
        q_1  = q_mf[0]
        q_B  = q_mf[1]
        qfb1  = q_mf[2]
        qab1  = q_mf[3]
        qwb1  = q_mf[4]
        phil1b1  = q_mf[5]
        qfb2  = q_mf[6]
        qab2  = q_mf[7]
        qwb2  = q_mf[8]
        phil1b2  = q_mf[9]
        
        u_B = u_mf[0]
        u1b1 = u_mf[1]
        u2 = u_mf[2]
        u1b2 = u_mf[3] 
        # data
        q_1_0 = self.q_1_0
        q_B_0 = self.q_B_0
        v_c_u_0 = self.v_c_u_0
        v_c_1_0 = self.v_c_1_0

        # Parameters
        c_1 = self.c_1
        R_0 = self.R_0
        R_1 = self.R_1
        v_a = self.v_a
        Q_0 = self.Q_0
        beta = self.beta
        v_N = self.v_N

        # rename things to use methods below
        u_B = u_s

        state_dim = self.state_dim
        # normally you would use mean field inputs here, but we are using local ones until the mean field is ready 
        qp_rhs_H_mf = self.qp_rhs_H_mf(q_mf, p_mf, u_mf, u_s)
        
        q_rhs_H_mf = qp_rhs_H_mf[:state_dim]
        p_rhs_H_mf = qp_rhs_H_mf[state_dim:]

        qp_rhs_H_l = self.qp_rhs_H_l(q_s, p_l, u_s, lambda_l)
        q_rhs_H_l = qp_rhs_H_l[:state_dim]
        p_rhs_H_l = qp_rhs_H_l[state_dim:]

        q_s_dot = self.gamma*p_rhs_H_mf + (1-self.gamma)*p_rhs_H_l
        p_mf_dot = q_rhs_H_mf
        p_l_dot = -1*q_rhs_H_l

        return np.concatenate([q_s_dot, p_l_dot, p_mf_dot])
 
    def u_rhs(self, t, u_vec, **kwargs):
        u_s = kwargs['u_0']
        q_mf_dot = kwargs['q_mf_dot']
        q_s_dot = kwargs['q_s_dot']
        p_l_dot = kwargs['p_l_dot']
        p_mf_dot = kwargs['p_mf_dot']
        q_mf = kwargs['q_mf']
        u_mf = kwargs['u_mf']
        qp_vec = kwargs['qp_vec']
        H_l_D = kwargs['H_l_D']
        Beta_mf = kwargs['Beta_mf']
        Beta_l = kwargs['Beta_l']
        alpha_mf = kwargs['alpha_mf']
        alpha_l = kwargs['alpha_l']
        state_dim = self.state_dim
        q_s = qp_vec[:state_dim]
        p_l = qp_vec[state_dim:2*state_dim]
        p_mf = qp_vec[2*state_dim:]
        u_s_dot = np.array([])
        for j in range(self.control_dim):
            '''for each control, we need to:
                1) Compute and get a 1D np.array for each of alpha_l_j, etc.
                2) Compute u_s_dot_j = -1*self.Gamma*(self.gamma*(alpha_mf_j + np.dot(Beta_mf_j, u_s)) + (1-self.gamma)*(alpha_l_j + np.dot(Beta_l_j,u_s)))
                3) Concatenate all of the u_s_dot_j to construct u_s_dot in a 1D np.array
            '''
            Beta_mf_j,Beta_l_j = Beta_mf[j], Beta_l[j] 
            alpha_mf_j, alpha_l_j = alpha_mf[j], alpha_l[j]
            # Beta_mf_j, Beta_l_j should be vectors
            # alpha_mf_j, alpha_l_j should be scalars
            u_s_dot_j = -1*self.Gamma*(self.gamma*(alpha_mf_j + np.dot(Beta_mf_j, u_s)) + (1-self.gamma)*(alpha_l_j + np.dot(Beta_l_j,u_s)))
            u_s_dot=np.concatenate([u_s_dot, np.array([u_s_dot_j])])
        
        return u_s_dot

## --- remove because Shen said she will pass to you as input ---
#    def H_D(self, q_1, q_B, p_1, p_B, u_B, q_1_0, q_B_0, v_c_u_0, v_c_1_0, c_1, R_0, R_1, v_a, Q_0, beta, v_N, q_1_prev, q_B_prev, v_c_1_prev, v_c_u_prev):
#        # TODO: replace as a function of self.K and self.T
#        delta = 1
#        term_1 = 0.5*((p_B - p_1)/(R_0*delta)) + 0.5*((p_1)**2)/(R_1*delta) 
#        term_2 = (c_1/2)*((((q_1 - q_1_prev)/c_1) + v_c_1_prev)**2 - (v_c_1**2))
#        term_3 = 0.5*(u_B*(-(q_B - q_B_prev)**2)+2*(-(q_B-q_B_prev)*v_c_u_prev))
#        term_4 = (v_N/(beta**2))*(beta*q_B - beta*q_B_prev + (Q_0*beta - Q_0)*np.log((Q_0 - Q_0*beta + beta*q_B)/(Q_0 - Q_0*beta + beta*q_B_prev)))
#        term_5 = -(q_B - q_B_prev)*v_a
#        H_D = term_1 + term_2 + term_3 + term_4 + term_5
#        return H_D
        
