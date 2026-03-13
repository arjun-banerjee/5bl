import os,numpy as np,matplotlib.pyplot as plt
from scipy.stats import linregress

os.makedirs('figures',exist_ok=True)
dy=0.005

def plot_ohm(v,i,dy,t,fn,c):
    
    n=len(v)
    m,b,_,_,dm=linregress(v,i)
    db=dm*np.sqrt(np.sum(v**2)/n)
    ifit=m*v+b
    res=i-ifit
    chi2=np.sum((res/dy)**2)/(n-2)
    
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(8,8),gridspec_kw={'height_ratios':[3,1]},sharex=True)
    
    ax1.errorbar(v,i,yerr=dy,fmt='o',color=c,label='Data',capsize=4)
    lbl=f'Fit: I = ({m:.4f} $\\pm$ {dm:.4f}) V + ({b:.4f} $\\pm$ {db:.4f})\n$\\chi^2_\\nu$ = {chi2:.2f}'
    ax1.plot(v,ifit,color='black',linestyle='--',label=lbl)
    ax1.set_title(t,fontsize=14)
    ax1.set_ylabel('Current (mA)',fontsize=12)
    ax1.grid(True)
    ax1.legend(fontsize=11)
    
    ax2.errorbar(v,res,yerr=dy,fmt='o',color=c,capsize=4)
    ax2.axhline(0,color='black',linestyle='--')
    ax2.set_xlabel('Voltage / DAC (V)',fontsize=12)
    ax2.set_ylabel('Residuals (mA)',fontsize=12)
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(fn,dpi=300,bbox_inches='tight')
    plt.close()

ir=np.array([0.01,0.04,0.08,0.10,0.13,0.16,0.195,0.22,0.26,0.29,0.33])
vr=np.array([0.1,0.4,0.7,1.0,1.3,1.6,1.9,2.2,2.5,2.9,3.3])-ir*1
plot_ohm(vr,ir,dy,'Resistor (Ohmic)','figures/resistor_fit.png','blue')


ig=np.array([0.01,0.02,0.025,0.035,0.05,0.06,0.07,0.10,0.10,0.12])
vg=np.array([2.1,2.2,2.3,2.4,2.5,2.7,2.9,3.1,3.2,3.3])-ig*1
plot_ohm(vg,ig,dy,'Green LED (Non-Ohmic)','figures/green_led_fit.png','green')


ired=np.array([0.005,0.01,0.02,0.03,0.05,0.07,0.08,0.11,0.13,0.15,0.16])
vred=np.array([1.6,1.7,1.8,2.0,2.2,2.4,2.5,2.8,3.0,3.2,3.3])-ired*1
plot_ohm(vred,ired,dy,'Red LED (Non-Ohmic)','figures/red_led_fit.png','red')

m_r, _, _, _, dm_r = linregress(vr, ir)
R_r, dR_r = 1 / m_r, dm_r / (m_r**2)
print(f"Resistor: R = {R_r:.2f} Ω ± {dR_r:.2f} Ω")

m_g, _, _, _, dm_g = linregress(vg, ig)
R_g, dR_g = 1 / m_g, dm_g / (m_g**2)
print(f"Green LED: R = {R_g:.2f} Ω ± {dR_g:.2f} Ω")

m_red, _, _, _, dm_red = linregress(vred, ired)
R_red, dR_red = 1 / m_red, dm_red / (m_red**2)
print(f"Red LED: R = {R_red:.2f} Ω ± {dR_red:.2f} Ω")