### Using plotly library ###
import numpy as np
import pandas as pd
import plotly.graph_objects as go

##DATA HANDLING
fulldata = np.genfromtxt('outputs/0100_t03_2_TMAP_p20_i5-ig/results.csv',skip_header = 1, delimiter = ',') #results from running models
tdata = np.transpose(fulldata)
masses = tdata[0]
periods = tdata[1]
incls = tdata[2]
ohs = tdata[4]
ecs = tdata[6]

## PLotting
fig = go.Figure()


#making array so only 1st mass is visible orginally on plot
is_vis = []
for u in range(15): #15 masses for CARMENES
    if u == 0:
        is_vis.append(True)
    else:
        is_vis.append(False)

#adding surface for the observational limit of 0.1 mag
x, y ,z= np.linspace(0, 10, 100), np.linspace(0, 90, 100), 0.1*np.ones((100,100))
mycolorscale = [[0.1, '#aa9ce2'],
                [1, '#aa9ce2']]
fig.add_trace(
    go.Surface(x=x, y=y, z=z, showscale=False,hoverinfo='skip',opacity=0.5,showlegend=True,
               name='Ground-based Dectection Limit (0.1 mag)',visible=True, colorscale=mycolorscale,
               )
)

distinct_masses = []

#colorscales = ['viridis','ylgn','ylgnbu','ylorbr','ylorrd','algae','amp','deep',
#'dense','gray','haline','ice','matter','solar','speed' ] used to check it was plotting different surfaces

#extracting the data for each mass and plotting them
for n in range(15):#15 masses for CARMENES

    j = n*380

    m = round(masses[j],4)

    try:
        p = periods[j:j+379]
        ic = incls[j:j+379]
        a = ohs[j:j+379]
        e = ecs[j:j+379]
    except:
        p = periods[j:]
        ic = incls[j:]
        a = ohs[j:]
        e = ecs[j:]

    emask = (e!=0)

    p1 = p[~emask]
    i1 = ic[~emask]
    a1 = a[~emask]


    p2 = p[emask]
    i2 = ic[emask]
    a2 = a[emask]

    distinct_masses.append(m) #adds mass to list so can use it in title

    fig.add_trace( #surface constructed from points
    go.Mesh3d(x=p, y=ic, z=a, colorscale = "emrld",
              intensity=a, showscale=False,
              hoverinfo='skip', visible = is_vis[n]
             ))

    fig.add_trace( #scatter plots are only used for the hover text now (so opacity is very low)
        go.Scatter3d( #plot non-eclipsing data
            x = p1,
            y = i1,
            z = a1,
            mode='markers',
            marker = dict(size =20, color='deepskyblue',opacity=0.000001),
            hovertemplate ="Period: %{x} days"+ #format of box when you hover over point
             "<br>Inclination: %{y} degs<br>"+
              "Amplitude: %{z} mag",
            name = 'Not Eclipsing',
            showlegend = False,
            visible = is_vis[n] #makes it so only 1st mass is visible on startup
            ))
    fig.add_trace( #sam but for plotting eclipsing data (different colour and label)
        go.Scatter3d(
            x = p2,
            y = i2,
            z = a2,
            mode='markers',
            marker = dict(size =20,color='hotpink',opacity=0.000001),
            hovertemplate ="Period: %{x} days"+
             "<br>Inclination: %{y} degs<br>"+
              "Amplitude: %{z} mag",
            name = 'Eclipsing',
            showlegend = False,
            visible = is_vis[n]
            ))


#spectral types corresponding to mass (as strings)
sp_types = np.genfromtxt('CARMENES_info-extended.csv',skip_header = 1, delimiter = ',',usecols = (0),dtype=str)

#makes the lists for the options for the dropdown menu
buts = []
for i in range(15): #15 masses for CARMENS in extended version
    k = i*3
    vis = np.array(False*np.ones(46),dtype=bool) #46 (=15*3 +1) 15 plots with 3 traces plus one plane
    vis[0], vis[k+1], vis[k+2], vis[k+3] = True, True, True, True #makes 1st and 3 adjacent indices True so plane,surface, non-eclipsing and eclipsing data for the mass are shown when the option is selected

    but = dict(label = sp_types[i],
                  method = 'update',
                  args = [{'visible': vis}, # the index of True aligns with the indices of plot traces
                          {'title': f'{sp_types[i]} Secondary Star (Mass = {distinct_masses[i]} solMass)',
                           'showlegend':True}])
    buts.append(but) #adds dropdown option to drop down list


fig.update_layout(
    updatemenus=[go.layout.Updatemenu(active=0,buttons=list(buts))], #adds dropdown menu
    title={'text':f'{sp_types[0]} Secondary Star (Mass = {distinct_masses[0]} solMass)'},
    legend=dict(yanchor="top", y=1.05,xanchor="center",x=0.5)) #moves legend below dropdown
    #makes first mass the title on start up, as that is the one shown (otherwise no title)

#configuring the axes labels
fig['layout']['scene']['xaxis']['title']='Period (days)'
fig['layout']['scene']['yaxis']['title']='Inclination (degs)'
fig['layout']['scene']['zaxis']['title']='Amplitude (mag)'

#shows graph and saves it in HTML format
fig.show()
fig.write_html("outputs/CARMENES_surface.html")
