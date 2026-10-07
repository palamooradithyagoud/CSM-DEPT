from flask import Blueprint, request
from app.models.department import (
    DepartmentInfo,
    FacultyMember,
    DepartmentEvent,
    StudentAchievement,
    Announcement,
)
from app.utils.response import api_response, api_error

public_bp = Blueprint("public", __name__)


@public_bp.route("/department-info", methods=["GET"])
def get_department_info():
    """Get core public department identity, vision, mission, and leadership message."""
    info = DepartmentInfo.query.first()
    if not info:
        return api_error(message="Department details not configured.", status_code=404)
    return api_response(data={"department": info.to_dict()})


@public_bp.route("/faculty", methods=["GET"])
def get_faculty():
    """
    Get faculty members directory.
    Optional query params: ?designation=Professor&search=name
    """
    query = FacultyMember.query.filter_by(is_active=True).order_by(FacultyMember.display_order.asc(), FacultyMember.name.asc())

    designation = request.args.get("designation")
    if designation:
        query = query.filter(FacultyMember.designation.ilike(f"%{designation}%"))

    search = request.args.get("search")
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (FacultyMember.name.ilike(search_term)) |
            (FacultyMember.specialization.ilike(search_term)) |
            (FacultyMember.qualification.ilike(search_term))
        )

    faculty_list = [f.to_dict() for f in query.all()]
    return api_response(data={"faculty": faculty_list, "total": len(faculty_list)})


@public_bp.route("/faculty/<faculty_id>", methods=["GET"])
def get_faculty_detail(faculty_id):
    """Get single faculty member details."""
    member = FacultyMember.query.get(faculty_id)
    if not member or not member.is_active:
        return api_error(message="Faculty profile not found.", status_code=404)
    return api_response(data={"faculty": member.to_dict()})


@public_bp.route("/events", methods=["GET"])
def get_events():
    """
    Get department events, workshops, hackathons, and symposiums.
    Optional query params: ?category=Workshop&upcoming=true
    """
    query = DepartmentEvent.query.order_by(DepartmentEvent.event_date.desc())

    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)

    upcoming = request.args.get("upcoming")
    if upcoming is not None:
        is_upcoming = upcoming.lower() in ("true", "1", "yes")
        query = query.filter_by(is_upcoming=is_upcoming)

    events_list = [e.to_dict() for e in query.all()]
    return api_response(data={"events": events_list, "total": len(events_list)})


@public_bp.route("/achievements", methods=["GET"])
def get_achievements():
    """
    Get public student achievements (Hackathons, Patents, Competitions, Publications).
    NEVER exposes individual CGPA, marks, or attendance.
    """
    category = request.args.get("category")
    query = StudentAchievement.query.order_by(StudentAchievement.achievement_date.desc())
    if category:
        query = query.filter_by(category=category)

    achievements_list = [a.to_dict() for a in query.all()]
    return api_response(data={"achievements": achievements_list, "total": len(achievements_list)})


@public_bp.route("/announcements", methods=["GET"])
def get_announcements():
    """Get official department announcements, circulars, and exam notices."""
    category = request.args.get("category")
    query = Announcement.query.order_by(Announcement.is_pinned.desc(), Announcement.publish_date.desc())
    if category:
        query = query.filter_by(category=category)

    announcements_list = [a.to_dict() for a in query.all()]
    return api_response(data={"announcements": announcements_list, "total": len(announcements_list)})


@public_bp.route("/stats", methods=["GET"])
def get_public_stats():
    """
    Get high-level public department statistics.
    Strictly aggregate & institutional metrics (Zero private student data).
    """
    total_faculty = FacultyMember.query.filter_by(is_active=True).count()
    total_events = DepartmentEvent.query.count()
    total_achievements = StudentAchievement.query.count()

    stats = {
        "facultyCount": total_faculty,
        "specializedLabs": 8,
        "studentIntake": 180,
        "eventsOrganized": total_events,
        "majorAchievements": total_achievements,
        "nbaAccredited": True,
        "naacRating": "A++",
        "establishedYear": 2008,
    }
    return api_response(data={"stats": stats})


@public_bp.route("/programs", methods=["GET"])
def get_programs():
    """
    Get academic degree programs offered by the department.
    Clearly structured academic offerings.
    """
    programs = [
        {
            "id": "btech-cse",
            "name": "B.Tech in Computer Science & Engineering",
            "code": "UG-CSE",
            "degree": "Bachelor of Technology",
            "duration": "4 Years (8 Semesters)",
            "intake": 180,
            "overview": "Comprehensive undergraduate program covering foundational computing theory, algorithm design, systems software, and modern application development.",
            "coreTracks": [
                "Data Structures & Algorithms",
                "Operating Systems & Architecture",
                "Database Management Systems",
                "Computer Networks & Security",
                "Full-Stack Web & Cloud Systems"
            ],
            "careerDirections": [
                "Software Development Engineer",
                "Systems Architect",
                "Cloud Solutions Engineer",
                "Research & Higher Studies"
            ]
        },
        {
            "id": "btech-cse-aiml",
            "name": "B.Tech in CSE (Artificial Intelligence & Machine Learning)",
            "code": "UG-AIML",
            "degree": "Bachelor of Technology",
            "duration": "4 Years (8 Semesters)",
            "intake": 60,
            "overview": "Specialized curriculum combining core computer science fundamentals with neural networks, deep learning, computer vision, and cognitive computing.",
            "coreTracks": [
                "Mathematics for Machine Learning",
                "Deep Learning & Neural Architectures",
                "Natural Language Processing",
                "Computer Vision & Robotics",
                "MLOps & Scalable Inference"
            ],
            "careerDirections": [
                "AI/ML Engineer",
                "Data Scientist",
                "Computer Vision Specialist",
                "Applied Research Scientist"
            ]
        },
        {
            "id": "mtech-cse",
            "name": "M.Tech in Computer Science & Engineering",
            "code": "PG-CSE",
            "degree": "Master of Technology",
            "duration": "2 Years (4 Semesters)",
            "intake": 24,
            "overview": "Postgraduate program focused on advanced research methodologies, distributed high-performance computing, and cybersecurity paradigms.",
            "coreTracks": [
                "Advanced Distributed Systems",
                "Cryptographic Protocols & Blockchain",
                "Big Data Analytics & Streaming",
                "Doctoral Dissertation Research"
            ],
            "careerDirections": [
                "Principal Research Engineer",
                "Technical Architect",
                "Doctoral Researcher",
                "Engineering Leadership"
            ]
        },
        {
            "id": "phd-cse",
            "name": "Ph.D. in Computer Science & Engineering",
            "code": "DOC-CSE",
            "degree": "Doctor of Philosophy",
            "duration": "3 to 5 Years",
            "intake": 10,
            "overview": "Rigorous doctoral research program under distinguished faculty guidance in AI, Network Security, Big Data, and Distributed Computing.",
            "coreTracks": [
                "Machine Learning & Edge Intelligence",
                "Wireless Sensor Networks & IoT",
                "Cloud Security & Fault Tolerance",
                "Bioinformatics & Computational Biology"
            ],
            "careerDirections": [
                "University Professor",
                "Industrial R&D Director",
                "Principal Scientist"
            ]
        }
    ]
    return api_response(data={"programs": programs, "total": len(programs)})


@public_bp.route("/gallery", methods=["GET"])
def get_gallery():
    """
    Get departmental gallery items across categories.
    Categories: Events, Workshops, Seminars, Student Activities, Department Activities
    """
    category = request.args.get("category")
    gallery_items = [
        {
            "id": 1,
            "title": "National AI Conference Keynote Address",
            "category": "Events",
            "date": "2026-03-12",
            "imageUrl": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
            "description": "Distinguished plenary session on neural architectures in the main collegiate auditorium."
        },
        {
            "id": 2,
            "title": "Hands-on Microservices & Cloud Lab",
            "category": "Workshops",
            "date": "2026-02-28",
            "imageUrl": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80",
            "description": "Undergraduate students deploying containerized microservices in the High-Performance Computing Lab."
        },
        {
            "id": 3,
            "title": "Smart Campus 36-Hour Hackathon",
            "category": "Student Activities",
            "date": "2026-01-22",
            "imageUrl": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
            "description": "Inter-departmental student teams coding real-time telemetry prototypes."
        },
        {
            "id": 4,
            "title": "Invited Lecture on Cryptographic Engineering",
            "category": "Seminars",
            "date": "2025-11-18",
            "imageUrl": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
            "description": "Session delivered by industry cybersecurity architects on post-quantum cryptographic primitives."
        },
        {
            "id": 5,
            "title": "Annual Department Day & Scholar Awards",
            "category": "Department Activities",
            "date": "2025-10-30",
            "imageUrl": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
            "description": "Honoring academic top rankers and collegiate technical competition winners."
        },
        {
            "id": 6,
            "title": "Robotics & Edge Sensor Integration Session",
            "category": "Workshops",
            "date": "2025-09-14",
            "imageUrl": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80",
            "description": "Hardware programming on ESP32 microcontrollers and embedded cameras."
        }
    ]

    if category and category.lower() != "all":
        gallery_items = [g for g in gallery_items if g["category"].lower() == category.lower()]

    return api_response(data={"gallery": gallery_items, "total": len(gallery_items)})


@public_bp.route("/news", methods=["GET"])
def get_news():
    """
    Get departmental news items with thumbnails and read-more details.
    """
    news_items = [
        {
            "id": 1,
            "title": "Department Secures Rs. 45 Lakhs Research Grant for Edge AI Systems",
            "date": "2026-03-24",
            "category": "Research Grant",
            "imageUrl": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
            "summary": "The Department of CSE has been awarded a prestigious central research grant to establish a high-throughput Edge Computing and Embedded Vision testbed.",
            "content": "The Department of Computer Science & Engineering has received a competitive research grant sanctioned by the Department of Science and Technology (DST). Under the supervision of Dr. M. A. Jabbar, the funded research will focus on energy-constrained neural inference for smart healthcare monitoring systems."
        },
        {
            "id": 2,
            "title": "NBA Renews Tier-I Accreditation with Highest Qualitative Score",
            "date": "2026-02-15",
            "category": "Accreditation",
            "imageUrl": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80",
            "summary": "Following a comprehensive peer-review committee inspection, the undergraduate B.Tech CSE program has received a 3-year unconditional accreditation extension.",
            "content": "The National Board of Accreditation (NBA) expert evaluation team commended the department's structured outcome-based curriculum, robust student mentorship framework, subject-wise attendance analytics, and high faculty publication index."
        },
        {
            "id": 3,
            "title": "CSE Students Win 1st Prize at National Smart India Hackathon Finals",
            "date": "2025-12-20",
            "category": "Student Win",
            "imageUrl": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=600&q=80",
            "summary": "A six-member student development cohort from 2nd and 3rd year CSE secured first place along with a cash award of Rs. 1,00,000 for their offline telemetry application.",
            "content": "Competing against over 1,200 collegiate teams nationwide, the departmental team designed and demonstrated an offline-tolerant medical inventory tracking protocol leveraging peer-to-peer Wi-Fi mesh protocols."
        }
    ]
    return api_response(data={"news": news_items, "total": len(news_items)})

