import streamlit as st
import plotly.graph_objects as go
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading

# FastAPI app for REST API
api = FastAPI(title="Sunflower Phyllotaxis API", version="1.0.0")

# Pydantic models for API
class PhyllotaxisParams(BaseModel):
    num_points: int = 1000
    golden_angle_multiplier: float = 1.0
    radius: float = 10.0
    animation_frames: int = 100
    color_scheme: str = "blue_to_red"

class PhyllotaxisResponse(BaseModel):
    x_vals: list
    y_vals: list
    z_vals: list
    time_vals: list
    color_vals: list
    frames: list

def generate_sunflower_data(params: PhyllotaxisParams):
    golden_angle = np.pi * (3 - np.sqrt(5)) * params.golden_angle_multiplier
    time_embeddings = np.linspace(0, 1, params.num_points)
    x_vals, y_vals, z_vals, time_vals, color_vals = [], [], [], [], []
    
    for i, t in enumerate(time_embeddings):
        angle = i * golden_angle
        z = 1 - (2 * i) / params.num_points
        radius_at_z = np.sqrt(1 - z**2)
        x = radius_at_z * np.cos(angle) * params.radius
        y = radius_at_z * np.sin(angle) * params.radius
        
        if params.color_scheme == "blue_to_red":
            r = int(255 * t)
            g = int(100 * (1 - t))
            b = int(255 * (1 - t))
        elif params.color_scheme == "rainbow":
            hue = t * 360
            r = int(255 * (1 - abs((hue / 60) % 2 - 1)) if hue < 120 else 255 * (1 - t))
            g = int(255 * t if hue < 120 else 255 * (1 - abs((hue / 60) % 2 - 1)))
            b = int(255 * (1 - t) if hue < 240 else 255 * t)
        elif params.color_scheme == "green_to_purple":
            r = int(128 + 127 * t)
            g = int(255 * (1 - t))
            b = int(128 + 127 * t)
        
        color = f'rgba({r}, {g}, {b}, 0.9)'
        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z * params.radius)
        time_vals.append(t)
        color_vals.append(color)
    
    frames = []
    for angle in np.linspace(0, 360, params.animation_frames):
        camera_eye = {
            'x': 1.5 * np.cos(np.radians(angle)),
            'y': 1.5 * np.sin(np.radians(angle)),
            'z': 1
        }
        frames.append(camera_eye)
    
    return {
        'x_vals': x_vals,
        'y_vals': y_vals,
        'z_vals': z_vals,
        'time_vals': time_vals,
        'color_vals': color_vals,
        'frames': frames
    }

def create_plotly_figure(data):
    frames = []
    for i, camera_eye in enumerate(data['frames']):
        frames.append(go.Frame(
            layout=dict(scene_camera=dict(eye=camera_eye)),
            name=str(i)
        ))
    
    fig = go.Figure(
        data=[go.Scatter3d(
            x=data['x_vals'], 
            y=data['y_vals'], 
            z=data['z_vals'],
            mode='markers',
            marker=dict(size=5.25, color=data['color_vals'], opacity=0.9),
            text=[f'Time: {round(t, 2)}' for t in data['time_vals']],
            hoverinfo='text'
        )]
    )
    
    fig.update(frames=frames)
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor='black',
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='black',
        height=600,
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate',
                 'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True}]},
                {'label': 'Pause', 'method': 'animate',
                 'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}]}
            ]
        }]
    )
    
    return fig

# API Endpoints
@api.get("/")
def read_root():
    return {"message": "Sunflower Phyllotaxis API", "version": "1.0.0"}

@api.post("/generate", response_model=PhyllotaxisResponse)
def generate_phyllotaxis(params: PhyllotaxisParams):
    try:
        data = generate_sunflower_data(params)
        return PhyllotaxisResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/presets/{preset_name}")
def get_preset(preset_name: str):
    presets = {
        "classic": PhyllotaxisParams(num_points=1000, golden_angle_multiplier=1.0, radius=10.0),
        "dense": PhyllotaxisParams(num_points=2000, golden_angle_multiplier=1.0, radius=8.0),
        "spiral": PhyllotaxisParams(num_points=1500, golden_angle_multiplier=1.2, radius=12.0),
        "tight": PhyllotaxisParams(num_points=800, golden_angle_multiplier=0.8, radius=6.0)
    }
    
    if preset_name not in presets:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    return presets[preset_name]

# Streamlit Dashboard
def main():
    st.set_page_config(
        page_title="Sunflower Phyllotaxis Dashboard",
        page_icon="🌻",
        layout="wide"
    )
    
    # Sidebar controls
    num_points = st.sidebar.slider("Number of Points", 100, 3000, 1000, 50)
    golden_angle_mult = st.sidebar.slider("Golden Angle Multiplier", 0.5, 2.0, 1.0, 0.1)
    radius = st.sidebar.slider("Radius", 5.0, 20.0, 10.0, 0.5)
    animation_frames = st.sidebar.slider("Animation Frames", 50, 200, 100, 10)
    color_scheme = st.sidebar.selectbox(
        "Color Scheme",
        ["blue_to_red", "rainbow", "green_to_purple"],
        index=0
    )
    
    # Main visualization
    params = PhyllotaxisParams(
        num_points=num_points,
        golden_angle_multiplier=golden_angle_mult,
        radius=radius,
        animation_frames=animation_frames,
        color_scheme=color_scheme
    )
    
    with st.spinner("Generating visualization..."):
        data = generate_sunflower_data(params)
        fig = create_plotly_figure(data)
        st.plotly_chart(fig, use_container_width=True)

def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    main()