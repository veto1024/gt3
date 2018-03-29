# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 16:05:08 2017

@author: max
"""

from math import pi,sin,acos
import numpy as np
from scipy.constants import mu_0, elementary_charge, k
from helpers import PolyArea
from scipy.interpolate import UnivariateSpline, interp1d
from scipy.integrate import quad
import matplotlib.pyplot as plt

class background():
    """Calculates various plasma properties using a modified Miller geometry
    
    Methods:
        createbackround
        xmiller
    
    Attributes:
        r
        theta
        rho
        ni
        ne
        Ti_kev
        Ti_K
        Ti_J
        Te_kev
        Te_K
        Te_J
        nC
        E_pot
        pressure
        j_r
        kappa
        tri
        R
        Z
        diff_vol
        IP
        B_phi
        Psi
        Psi_norm
        B_p
        B_tot
        f_phi
    """
    def __init__(self,parameters):
        self.createbackground(parameters)

    def createbackground(self,p):
        """Create background plasma using the miller model.
        
        Note:
            
        Args:
        """
        ## CREATE r AND theta MATRICES
        r1d = np.linspace(0,p.a,p.rpts)
        theta1d = np.linspace(0,2*pi,p.thetapts)
        self.theta, self.r = np.meshgrid(theta1d,r1d)
        self.rho = self.r/self.r[-1,0]

        ##########################################################################################
        ## CREATE DENSITY, TEMPERATURE, PRESSURE, AND CURRENT DENSITY ARRAYS
        ##########################################################################################
        if hasattr(p, 'ni_file'):
            self.ni = interp1d(p.ni_rho[:,0],p.ni_rho[:,1])(self.rho)
        else:
            self.ni = np.where(self.r<0.9*p.a,
                               (p.ni0-p.ni9)*(1-self.rho**2)**p.nu_ni + p.ni9,
                               (p.ni_sep-p.ni9)/(0.1*p.a)*(self.r-0.9*p.a)+p.ni9)

        #############################################

        if hasattr(p, 'ne_file'):
            self.ne = interp1d(p.ne_rho[:,0],p.ne_rho[:,1])(self.rho)
        else:
            self.ne = np.where(self.r<0.9*p.a,
                               (p.ne0-p.ne9)*(1-self.rho**2)**p.nu_ne + p.ne9,
                               (p.ne_sep-p.ne9)/(0.1*p.a)*(self.r-0.9*p.a)+p.ne9)
    
        #############################################

        if hasattr(p, 'fracz_file'):
            #TODO: verify that this is how fracz is defined
            self.fracz = interp1d(p.fracz_rho[:,0],p.fracz_rho[:,1])(self.rho)
        else:
            self.fracz = np.zeros(self.rho.shape) + 0.025     
            
        self.nC = self.ne * self.fracz   

        #############################################

        if hasattr(p, 'Ti_file'):
            self.Ti_kev = interp1d(p.Ti_rho[:,0],p.Ti_rho[:,1])(self.rho)
        else:
            self.Ti_kev = np.where(self.r<0.9*p.a,
                             (p.Ti0-p.Ti9)*(1-self.rho**2)**p.nu_Ti + p.Ti9,
                             (p.Ti_sep-p.Ti9)/(0.1*p.a)*(self.r-0.9*p.a)+p.Ti9)
        self.Ti_K  = self.Ti_kev * 1.159E7
        self.Ti_ev = self.Ti_kev * 1000
        self.Ti_J  = self.Ti_ev  * elementary_charge


        #############################################

        if hasattr(p, 'Te_file'):
            self.Te_kev = interp1d(p.Te_rho[:,0],p.Te_rho[:,1])(self.rho)
        else:            
            self.Te_kev = np.where(self.r<0.9*p.a,
                             (p.Te0-p.Te9)*(1-self.rho**2)**p.nu_Te + p.Te9,
                             (p.Te_sep-p.Te9)/(0.1*p.a)*(self.r-0.9*p.a)+p.Te9) 
        self.Te_K  = self.Te_kev * 1.159E7
        self.Te_ev = self.Te_kev * 1000
        self.Te_J  = self.Te_ev  * elementary_charge

        #############################################

        if hasattr(p, 'er_file'):
            E_r_fit = UnivariateSpline(p.er_rho[:,0], p.er_rho[:,1])
            self.E_r = E_r_fit(self.rho)
            
            self.E_pot = np.zeros(self.r.shape)
            for (i,j),rval in np.ndenumerate(self.r):
                self.E_pot[i,j] = E_r_fit.integral(rval/p.a, 1.0)
        else:
            print 'You need E_r data'
            sys.exit()

        #############################################

        if hasattr(p, 'jr_file'):
            pass
        else:
            self.j_r = p.j0*(1-(self.r/p.a)**2)**p.nu_j   

        #############################################

        if hasattr(p, 'fz1_file'):
            self.fz1 = interp1d(p.fz1_rho[:,0],p.fz1_rho[:,1])(self.rho)
        else:
            self.fz1 = 0.025*self.ne

        #############################################

        if hasattr(p, 'fracz_file'):
            self.fracz = interp1d(p.fracz_rho[:,0],p.fracz_rho[:,1])(self.rho)
        else:
            self.fracz = np.zeros(self.rho)+0.025

        #############################################

        if hasattr(p, 'exlti_file'):
            self.exlti = interp1d(p.exlti_rho[:,0],p.exlti_rho[:,1])(self.rho)
        else:
            self.exlti = 0.0

        #############################################

        if hasattr(p, 'exlte_file'):
            self.exlte = interp1d(p.exlte_rho[:,0],p.exlte_rho[:,1])(self.rho)
        else:
            self.exlte = 0.0

        #############################################

        if hasattr(p, 'exlni_file'):
            self.exlni = interp1d(p.exlni_rho[:,0],p.exlni_rho[:,1])(self.rho)
        else:
            self.exlni = 0.0

        #############################################

        if hasattr(p, 'vpolC_file'):
            self.vpolC = interp1d(p.vpolC_rho[:,0],p.vpolC_rho[:,1])(self.rho)
        else:
            self.vpolC = 0.0

        #############################################

        if hasattr(p, 'vtorC_file'):
            self.vtorC = interp1d(p.vtorC_rho[:,0],p.vtorC_rho[:,1])(self.rho)
        else:
            self.vtorC = 0.0

        #############################################

        if hasattr(p, 'vpolD_file'):
            self.vpolD = interp1d(p.vpolD_rho[:,0],p.vpolD_rho[:,1])(self.rho)
        else:
            self.vpolD = 0.0

        #############################################

        if hasattr(p, 'vtorD_file'):
            self.vtorD = interp1d(p.vtorD_rho[:,0],p.vtorD_rho[:,1])(self.rho)
        else:
            self.vtorD = 0.0
        #############################################

        if hasattr(p, 'q_file'):
            self.q = interp1d(p.q_rho[:,0],p.q_rho[:,1])(self.rho)
        else:
            self.q = np.zeros(self.rho.shape) #will calculated later with the other miller stuff

        #############################################

        if hasattr(p, 'zbar2_file'):
            self.zbar2 = interp1d(p.zbar2_rho[:,0],p.zbar2_rho[:,1])(self.rho)
        else:
            self.zbar2 = np.zeros(self.rho.shape) + 0.025


        self.pressure = self.ni * k * self.Ti_K
        
        ##########################################################################################
        ## CREATE kappa, tri AND RELATED MATRICES
        ##########################################################################################
        upperhalf   = (self.theta>=0)&(self.theta<pi)
        #self.kappa  = np.where(upperhalf, 
        #                 p.kappa_up / (p.a**p.s_k_up) * self.r**p.s_k_up,
        #                 p.kappa_lo / (p.a**p.s_k_lo) * self.r**p.s_k_lo)
        
        
        ## All we're doing with kappa in this next part is making the derivative between upper and lower
        ## elongation continuous by "smoothing out" the "step function"
        ## using f(x) = tanh(B*sin(x)), where be controlls how smooth or squre the function is.
        ## Plot that function and you'll see what we're doing. This is necessary 
        ## to prevent shafranov shift from producing ugly pictures with high poloidal
        ## resolution. It also makes Richard's stuff easier. Just deal with it 
        ## and don't put this in any papers. It's just a bandaid. We do the same 
        ## thing with triangularity. - MH
        B_kappa = 0.0
        self.kappa  = (((p.kappa_up / (p.a**p.s_k_up) * self.r**p.s_k_up) - (p.kappa_lo / (p.a**p.s_k_lo) * self.r**p.s_k_lo))/2.0 
                * np.tanh(B_kappa*np.sin(self.theta))
                + ((p.kappa_up / (p.a**p.s_k_up) * self.r**p.s_k_up) + (p.kappa_lo / (p.a**p.s_k_lo) * self.r**p.s_k_lo))/2.0)
         
        if p.xmil==1:               
            self.kappa = self.xmiller(self.kappa,p)
            tri_lo = sin(3*pi/2 - acos((p.xpt[0]-p.R0_a)/p.a))
            tri_up = p.tri_up
        else:
            tri_lo = p.tri_lo
            tri_up = p.tri_up
            

        tri    = np.where(upperhalf,
                         tri_up * (self.r/p.a)**1,
                         tri_lo * (self.r/p.a)**1)

        s_tri  = np.where(upperhalf,
                         self.r*p.tri_up/(p.a*np.sqrt(1-tri)),
                         self.r*tri_lo/(p.a*np.sqrt(1-tri)))
        
        ## MODIFY kappa USING THE X-MILLER MODEL
        
        
        ## CALCULATE INITIAL R,Z WITH NO SHAFRANOV SHIFT
        ## (NECESSARY TO GET ESTIMATES OF L_r WHEN CALCULATING SHAFRANOV SHIFT)
        R0 = np.ones(self.r.shape) * p.R0_a 
        self.R = R0 + self.r * np.cos(self.theta+np.arcsin(tri*np.sin(self.theta)))
        self.Z = self.kappa*self.r*np.sin(self.theta)
        
        # THIS CALCULATES A MATRIX OF THE LENGTHS OF EACH SECTION OF EACH FLUX
        # SURFACE AND THEN SUMS THEM TO GET THE PERIMETER IN 2D OF EACH FLUX
        # SURFACE (VALUE OF r).
        self.L_seg = np.sqrt((self.Z-np.roll(self.Z,-1,axis=1))**2 + (self.R-np.roll(self.R,-1,axis=1))**2)
        self.L_seg [:,-1] = 0        
        self.L_r = np.tile(np.sum(self.L_seg, axis=1), (p.thetapts, 1)).T
        
        #CALCULATE CROSS-SECTIONAL AREA CORRESPONDING TO EACH r AND ASSOCIATED
        #DIFFERENTIAL AREAS
        area = np.zeros(self.r.shape)
        for i in range(0,p.rpts):
            area[i,:] = PolyArea(self.R[i,:],self.Z[i,:])
    
        diff_area = area - np.roll(area,1,axis=0)
        diff_area[0,:]=0
        
        self.diff_vol = diff_area * 2*pi*p.R0_a #approx because it uses R0_a instead of shifted R0
        vol = np.cumsum(self.diff_vol,axis=0)
        
        #Calculate each differential I and sum to get cumulative I
        j_r_ave = np.roll((self.j_r + np.roll(self.j_r,-1, axis=0))/2,1,axis=0)
        j_r_ave[0,:]=0
        diff_I = diff_area * j_r_ave
        I = np.cumsum(diff_I, axis=0)
        self.IP = I[-1,0]  
        
        #Calculate B_p_bar
        B_p_bar = mu_0 * I / self.L_r
        B_p_bar[0,:]=0
        
        #Calculate li
        li = (np.cumsum(B_p_bar**2 * self.diff_vol, axis=0) / vol) / (2*B_p_bar**2)
        li[0,:]=0
        
        #Calculate beta_p
        beta_p = 2*mu_0*(np.cumsum(self.pressure*self.diff_vol,axis=0)/vol-self.pressure) / B_p_bar**2
    
        #Calculate dR0dr
        self.dR0dr = np.zeros(self.r.shape)
        self.R0 = np.zeros(self.r.shape)
    
        f = 2*(self.kappa**2+1)/(3*self.kappa**2+1)*(beta_p+li/2)+1/2*(self.kappa**2-1)/(3*self.kappa**2+1)
        f[0,:] = f[1,:] ############ NEED TO REVISIT, SHOULD EXTRAPOLATE SOMEHOW
        
        self.dR0dr[-1,:] = -2.0*p.a*f[-1,:]/p.R0_a
        self.R0[-1,:] = p.R0_a
        
        for i in range(p.rpts-2,-1,-1):
            self.R0[i,:] = self.dR0dr[i+1,:] * (self.r[i,:]-self.r[i+1,:]) + R0[i+1,:]
            self.dR0dr[i,:] = -2.0*self.r[i,:]*f[i,:]/R0[i,:]
        
        #NOW USE UPDATED R0 AND dR0dr to get new R,Z.
        self.R = self.R0 + self.r * np.cos(self.theta+np.arcsin(tri*np.sin(self.theta)))
        self.Z = self.kappa*self.r*np.sin(self.theta) + p.Z0

        #RECALCULATE L_seg and L_r
        self.L_seg = np.sqrt((self.Z-np.roll(self.Z,-1,axis=1))**2 + (self.R-np.roll(self.R,-1,axis=1))**2)
        self.L_seg [:,-1] = 0        
        self.L_r = np.tile(np.sum(self.L_seg, axis=1), (p.thetapts, 1)).T
        
        ## RECALCULATE GRAD-r
        dkappa_dtheta   = np.gradient(self.kappa, edge_order=1)[1] * p.thetapts/(2*pi)
        dkappa_dr       = np.gradient(self.kappa, edge_order=1)[0] * p.rpts/p.a
    
        dkappa_dtheta[-1] = dkappa_dtheta[-2]
        dkappa_dr[-1] = dkappa_dr[-2]
    
        dZ_dtheta       = np.gradient(self.Z, edge_order=2)[1] * p.thetapts/(2*pi) #self.r*(self.kappa*np.cos(self.theta)+dkappa_dtheta*np.sin(self.theta))
        dZ_dr           = np.gradient(self.Z, edge_order=2)[0] * p.rpts/p.a #np.sin(self.theta)*(self.r*dkappa_dr + self.kappa)
        dR_dr           = np.gradient(self.R, edge_order=2)[0] * p.rpts/p.a #dR0dr - np.sin(self.theta + np.sin(self.theta)*np.arcsin(tri))*(np.sin(self.theta)*s_tri) + np.cos(self.theta+np.sin(self.theta)*np.arcsin(tri))
        dR_dtheta       = np.gradient(self.R, edge_order=2)[1] * p.thetapts/(2*pi) #-self.r*np.sin(self.theta+np.sin(self.theta)*np.arcsin(tri))*(1+np.cos(self.theta)*np.arcsin(tri))
    
        abs_grad_r = np.sqrt(dZ_dtheta**2 + dR_dtheta**2) / np.abs(dR_dr*dZ_dtheta - dR_dtheta*dZ_dr)
        
        ## WE WANT TO CALCULATE THE POLOIDAL FIELD STRENGTH EVERYWHERE
        ## THE PROBLEM IS THAT WE'VE GOT 2 EQUATIONS IN 3 UNKNOWNS. HOWEVER, IF WE ASSUME THAT THE POLOIDAL
        ## INTEGRAL OF THE FLUX SURFACE AVERAGE OF THE POLOIDAL MAGNETIC FIELD IS APPROX. THE SAME AS THE
        ## POLOIDAL INTEGRAL OF THE ACTUAL POLOIDAL MAGNETIC FIELD, THEN WE CAN CALCULATE THE Q PROFILE
        self.B_phi = p.B_phi_0 * self.R[0,0] / self.R
        
        #Calculate initial crappy guess on q
        q_mil = p.B_phi_0*self.R[0,0] / (2*pi*B_p_bar) * np.tile(np.sum(self.L_seg/self.R**2,axis=1), (p.thetapts, 1)).T #Equation 16 in the miller paper. The last term is how I'm doing a flux surface average
        q_mil[0,:]=q_mil[1,:]
        
        dPsidr = (p.B_phi_0 * self.R[0,0]) / (2*pi*q_mil)*np.tile(np.sum(self.L_seg/(self.R*abs_grad_r),axis=1), (p.thetapts, 1)).T
        
        self.Psi = np.zeros(self.r.shape)
        for index,row in enumerate(self.r):
            if index >= 1:
                self.Psi[index] = dPsidr[index]*(self.r[index,0]-self.r[index-1,0]) + self.Psi[index-1]
        self.Psi_norm = self.Psi / self.Psi[-1,0]
        
        self.B_p = dPsidr * 1/self.R * abs_grad_r
        self.B_p[0,:] = 0
        
        
        self.B_phi = p.B_phi_0 * self.R[0,0] / self.R
        self.B_tot = np.sqrt(self.B_p**2 + self.B_phi**2)
        self.f_phi = self.B_phi/self.B_tot
        #######################################################################
        ## CALCULATE ELECTRIC POTENTIAL FROM EXPERIMENTAL RADIAL ELECTRIC FIELD DATA
        

    def xmiller(self,kappa,p):
        """
        """
        ##########################################################################
        ## PART 1: SELECT CONVOLUTION KERNEL. WE'LL USE A STANDARD BUMP FUNCTION.
        ##########################################################################
        def bump(x,epsilon):
            """
            """
            #define eta0
            def eta0(x2):
                """
                """
                eta0 = np.where(np.logical_and((x2>-1),(x2<1)),   np.exp(-1.0/(1.0-np.power(np.abs(x2),2.0))),   0.)
                return eta0
            #calculate normalization coefficient
            C = quad(eta0, -1, 1)[0]
            #calculate eta_eps
            eta_eps = 1/epsilon/C*eta0(x/epsilon)
            return eta_eps  
            
        #############################################################            
        ## PART 2: DEFINE SEPERATRIX FUNCTION
        #############################################################          
        def kappa_sep(x,gamma1,gamma2):
            """
            """
            #Necessary kappa to get the z-value of the x-point
            kappa_x = (p.xpt[1]-p.Z0) / (p.a*sin(3.*pi/2.))
            # Amount of "extra" kappa needed at the x-point, i.e. kappa_tilda
            delta_kappa = kappa_x - p.kappa_lo
    
            kappa_sep = np.piecewise(
                                x,
                                [x <= pi, #condition 1
                                 np.logical_and((pi < x),(x <= 3.*pi/2.)), #condition 2
                                 np.logical_and(( 3.*pi/2. < x),(x <= 2.*pi)), #condition 3
                                 x>2*pi], #condition 4
                                 [lambda x: 0, #function for condition 1
                                  lambda x: delta_kappa*(1.-abs(2.*x/pi - 3.)**(1.0))**gamma1, #function for condition 2
                                  lambda x: delta_kappa*(1.-abs(2.*x/pi - 3.)**(1.0))**gamma2, #function for condition 3
                                  lambda x: 0] #function for condition 4
                                 )
            return kappa_sep  
        
        ##########################################################################
        ## PART 2: RESCALE THETA (OPTIONAL) (HOW QUICKLY TO DO YOU LIMIT
        ## THETA RANGE OF CONVLUTION, IF AT ALL)
        ##########################################################################
        def rescale_theta(theta,epsilon):
            """
            """
            return (theta-3*pi/2)/(1-epsilon)+3*pi/2
            
        ##########################################################################
        ## PART 3: DEFINE Y-SCALE (HOW QUICKLY DO FLUX SURFACES
        ## APPROACH THE SEPERATRIX AS A FUNCTION OF r)
        ##########################################################################
        def yscale(r,a):
            """
            """
            nu=10.0 #nu=10ish works well
            return np.power(r/a,nu) #* (xpt[1] / (a*sin(3.*pi/2.)) - kappa_lo)
            
        ##########################################################################
        ## PART 4: DEFINE EPSILON AS A RUNCTION OF r (HOW QUICKLY DO FLUX SURFACES
        ## GET 'POINTY' AS THEY APPROACH THE SEPERATRIX)
        ##########################################################################
        def calc_eps(r,a):
            """
            """
            D=2.0 #What is this?
            nu=3.0
            return D*(1-np.power(r/a,nu))
        ##########################################################################
        ## PART 5: POST TRANSFORM (SUBTRACT ENDPOINTS, ETC.)
        ##########################################################################
        def posttransform(x,f): #here x is from pi to 2pi
            """
            """
            f_pt = f - ((f[-1]-f[0])/(2*pi-pi) * (x-pi) + f[0])
            return f_pt
        
        #INITIALIZE KAPPA_TILDA ARRAY
        kappa_tilda = np.zeros(kappa.shape)
    
        #DEFINE POINTS FOR THE CONVOLUTION. THIS IS SEPARATE FROM THETA POINTS.
        xnum = 1001
        
        #DEFINE SEPERATRIX FUNCTION
        gamma1 = 3
        gamma2 = 0.5
        k_sep = kappa_sep(np.linspace(pi,2*pi,xnum),gamma1,gamma2)    
    
        #For each flux surface (i.e. r value)
        for i,rval in enumerate(self.r.T[0]):
            if rval < p.a:
                #Calculate epsilon
                epsilon = calc_eps(rval,p.a)
                #OPTIONALLY - modify domain to ensure a constant domain of compact support based on current epsilon
                scale_theta=0
                if scale_theta==1:
                    thetamod = rescale_theta(self.theta,epsilon)
                
                #define convolution kernel for the flux surface, eta_epsilon (eta for short)
                eta = bump(np.linspace(-1,1,xnum), epsilon)
                
                #scale eta. The convolution operation doesn't 
                scaled_eta = eta * yscale(rval,p.a)
                
                #convolve seperatrix function and bump function
                kappa_tilda_pre = np.convolve(k_sep,scaled_eta,'same')/((xnum-1)/2) #Still don't understand why we need to divide by this, but we definitely need to.
        
                #post processing
                kappa_tilda_post = posttransform(np.linspace(pi,2*pi,xnum),kappa_tilda_pre)
                
                #create a 1D interpolation function for everywhere except for the seperatrix
                kappa_tilda_f = interp1d(np.linspace(pi,2*pi,xnum),kappa_tilda_post,kind="linear")
                for j in range(0,kappa_tilda.shape[1]):
                    if self.theta[i,j] > pi and self.theta[i,j] <= 2*pi:
                        kappa_tilda[i,j] = kappa_tilda_f(self.theta[i,j])
            else:
                kappa_tilda_f = interp1d(np.linspace(pi,2*pi,xnum),k_sep,kind="linear")
                for j in range(0,kappa_tilda.shape[1]):
                    if self.theta[i,j] > pi and self.theta[i,j] <= 2*pi:
                        kappa_tilda[i,j] = kappa_tilda_f(self.theta[i,j])
        
        kappa = kappa + kappa_tilda
        return kappa