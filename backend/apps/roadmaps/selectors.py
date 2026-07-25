"""
apps/roadmaps/selectors.py
---------------------------------------------------------------
नयाँ आर्किटेक्चर: Coming Soon/Roadmap पेजका लागि छुट्टै Roadmap
डाटाबेस (RoadmapItem) प्रयोग नगरी, apps.projects को Project
डाटाबेसबाटै योजनामा/विकासमा/परीक्षणमा रहेका परियोजनाहरू तानिन्छ।
यसले Projects Page र Coming Soon Page लाई एउटै स्रोतमा राख्छ।
---------------------------------------------------------------
"""
from apps.projects.selectors import get_roadmap_projects

__all__ = ["get_roadmap_projects"]
