
from dataclasses import dataclass, field
from bakery import assert_equal
from drafter import *


# ==================================================
# WEBSITE DESIGN
# ==================================================

set_website_style("pico")

NAVY = "#172B43"
BLUE = "#35658F"
LIGHT_BLUE = "#EAF2F8"
LIGHT_GRAY = "#F4F6F8"
WHITE = "#FFFFFF"
GRAY = "#64748B"
GREEN = "#26734D"
YELLOW = "#A66A13"
RED = "#B33A3A"

ISSUE_TYPES = [
    "Road Damage",
    "Pothole",
    "Sidewalk Damage",
    "Broken Streetlight",
    "Drainage / Flooding",
    "Traffic Signal",
    "Other"
]

SEVERITY_OPTIONS = ["1", "2", "3", "4", "5"]

FREQUENCY_OPTIONS = [
    "Rarely",
    "Sometimes",
    "Often",
    "Constantly"
]

IMPACT_OPTIONS = ["1", "2", "3", "4", "5"]

SORT_OPTIONS = [
    "Overall Priority",
    "Highest Severity",
    "Most Reported"
]


# ==================================================
# DATACLASSES
# ==================================================

@dataclass
class InfrastructureReport:
    """Stores information about one infrastructure report."""
    issue_type: str
    location: str
    severity: int
    frequency: str
    impact: int
    description: str


@dataclass
class State:
    """Stores information that the website needs to remember."""
    reports: list[InfrastructureReport] = field(default_factory=list)
    selected_category: str = "All Categories"
    search_location: str = ""
    sort_option: str = "Overall Priority"
    status_message: str = "Welcome to Civic Infrastructure Tracker!"
    selected_report_index: int = 0


# ==================================================
# DESIGN HELPER FUNCTIONS
# ==================================================

def create_card(title: str, content: list) -> Div:
    """Creates a consistently styled white content card.

    Args:
        title: The heading displayed on the card.
        content: The components displayed inside the card.

    Returns:
        A styled Drafter Div.
    """
    return Div(
        Header(title, 3),
        *content,
        style_background_color=WHITE,
        style_color=NAVY,
        style_border="1px solid #DCE3EA",
        style_border_radius="12px",
        style_padding="20px",
        style_margin="12px 0"
    )


def create_page(
    state: State,
    title: str,
    subtitle: str,
    content: list
) -> Page:
    """Creates the common layout used across all website pages.

    Args:
        state: The current website state.
        title: The page heading.
        subtitle: A short page description.
        content: The main page components.

    Returns:
        A consistently styled Drafter Page.
    """
    current_page = ""

    if title == "Community Overview":
        current_page = "index"
    elif title == "Submit an Infrastructure Issue":
        current_page = "report_page"
    elif title in [
        "Incomplete Report",
        "Invalid Category",
        "Invalid Rating",
        "Invalid Frequency",
        "Report Successfully Submitted"
    ]:
        current_page = "report_page"
    elif title in [
        "Community Dashboard",
        "Report Not Found",
        "Infrastructure Report Details"
    ]:
        current_page = "dashboard_page"
    elif title == "Government Reports":
        current_page = "export_page"
    elif title == "About Civic Infrastructure Tracker":
        current_page = "about_page"

    navigation_items = [
        ("Home", "index"),
        ("Report an Issue", "report_page"),
        ("Dashboard", "dashboard_page"),
        ("Government Reports", "export_page"),
        ("About", "about_page")
    ]

    navigation = []

    for label, route_name in navigation_items:
        if route_name != current_page:
            navigation.append(
                Link(
                    label,
                    route_name,
                    style_color=WHITE,
                    style_background_color=BLUE,
                    style_padding="7px 11px",
                    style_margin="3px",
                    style_border_radius="6px",
                    style_text_decoration="none",
                    style_display="inline-block",
                    style_font_size="14px"
                )
            )

    page_content = [
        Div(
            Header("CIVIC INFRASTRUCTURE TRACKER", 2),
            Text("COMMUNITY INFRASTRUCTURE PORTAL"),
            style_background_color=NAVY,
            style_color=WHITE,
            style_padding="20px",
            style_border_radius="10px"
        ),

        Div(
            *navigation,
            style_background_color=LIGHT_BLUE,
            style_padding="8px",
            style_border_radius="8px",
            style_margin="10px 0"
        ),

        Div(
            Header(title, 1),
            Text(subtitle),
            style_background_color=WHITE,
            style_color=NAVY,
            style_padding="12px",
            style_margin="12px 0"
        )
    ]

    page_content.extend(content)

    page_content.append(
        Div(
            Text("CIVIC INFRASTRUCTURE TRACKER"),
            Text("A CISC106 Final Project"),
            style_background_color=NAVY,
            style_color=WHITE,
            style_padding="16px",
            style_border_radius="10px",
            style_margin="20px 0"
        )
    )

    return Page(state, page_content)


def create_stat_card(title: str, value: str) -> Div:
    """Creates a statistics card for the dashboard.

    Args:
        title: The statistic being displayed.
        value: The numerical value being displayed.

    Returns:
        A styled statistics card.
    """
    return Div(
        Header(value, 2),
        Text(title),
        style_background_color=LIGHT_BLUE,
        style_color=NAVY,
        style_border="1px solid #DCE3EA",
        style_border_radius="12px",
        style_padding="18px",
        style_margin="8px 0"
    )


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def classify_severity(severity: int) -> str:
    """Classifies an infrastructure report by severity.

    Args:
        severity: An integer from 1 to 5.

    Returns:
        A description of the report's severity.
    """
    if severity >= 4:
        return "High"
    elif severity >= 3:
        return "Moderate"
    else:
        return "Low"


def get_frequency_score(frequency: str) -> int:
    """Converts report frequency into a numerical score.

    Args:
        frequency: How frequently the issue occurs.

    Returns:
        A numerical frequency score.
    """
    if frequency == "Constantly":
        return 4
    elif frequency == "Often":
        return 3
    elif frequency == "Sometimes":
        return 2
    else:
        return 1


def count_similar_reports(
    report: InfrastructureReport,
    reports: list[InfrastructureReport]
) -> int:
    """Counts reports with the same issue type and location.

    Args:
        report: The report being evaluated.
        reports: All infrastructure reports.

    Returns:
        The number of matching reports.
    """
    count = 0

    for other_report in reports:
        if (other_report.issue_type == report.issue_type
                and other_report.location.lower() ==
                report.location.lower()):
            count = count + 1

    return count


def calculate_priority_score(
    report: InfrastructureReport,
    reports: list[InfrastructureReport]
) -> int:
    """Calculates a priority score for an infrastructure report.

    Args:
        report: The report being evaluated.
        reports: All submitted reports.

    Returns:
        A priority score. Higher scores indicate greater priority.
    """
    severity_points = report.severity * 2
    impact_points = report.impact
    frequency_points = get_frequency_score(report.frequency)

    popularity_points = count_similar_reports(
        report, reports
    ) * 2

    total_score = (
        severity_points
        + impact_points
        + frequency_points
        + popularity_points
    )

    return total_score


def get_sort_value(
    report: InfrastructureReport,
    reports: list[InfrastructureReport],
    sort_option: str
) -> int:
    """Gets the value used to rank an infrastructure report.

    Args:
        report: The report being evaluated.
        reports: All infrastructure reports.
        sort_option: The selected ranking method.

    Returns:
        A numerical value used for ranking.
    """
    if sort_option == "Highest Severity":
        return report.severity

    elif sort_option == "Most Reported":
        return count_similar_reports(report, reports)

    else:
        return calculate_priority_score(report, reports)


def rank_reports(
    reports: list[InfrastructureReport],
    sort_option: str
) -> list[InfrastructureReport]:
    """Ranks infrastructure reports from highest to lowest priority.

    Args:
        reports: The reports that need to be ranked.
        sort_option: The selected ranking method.

    Returns:
        A new list containing the reports in ranked order.
    """
    ranked_reports = reports.copy()

    for end in range(len(ranked_reports) - 1, 0, -1):
        for index in range(end):
            current_score = get_sort_value(
                ranked_reports[index], reports, sort_option
            )

            next_score = get_sort_value(
                ranked_reports[index + 1], reports, sort_option
            )

            if current_score < next_score:
                temporary_report = ranked_reports[index]
                ranked_reports[index] = ranked_reports[index + 1]
                ranked_reports[index + 1] = temporary_report

    return ranked_reports


def get_filtered_reports(
    reports: list[InfrastructureReport],
    category: str,
    location: str
) -> list[InfrastructureReport]:
    """Filters reports by infrastructure category and location.

    Args:
        reports: All submitted reports.
        category: The selected infrastructure category.
        location: The location being searched.

    Returns:
        A list containing only matching reports.
    """
    matching_reports = []

    for report in reports:
        category_matches = (
            category == "All Categories"
            or report.issue_type == category
        )

        location_matches = (
            location.strip().lower() in report.location.lower()
        )

        if category_matches and location_matches:
            matching_reports.append(report)

    return matching_reports


def create_csv_text(
    reports: list[InfrastructureReport]
) -> str:
    """Creates copyable CSV-formatted report data.

    Args:
        reports: All submitted infrastructure reports.

    Returns:
        A string containing CSV-formatted information.
    """
    csv_text = (
        "Issue Type,Location,Severity,Frequency,Impact,Description\n"
    )

    for report in reports:
        issue_type = report.issue_type.replace('"', '""')
        location = report.location.replace('"', '""')
        frequency = report.frequency.replace('"', '""')
        description = report.description.replace('"', '""')

        csv_text = csv_text + (
            '"' + issue_type + '",'
            + '"' + location + '",'
            + str(report.severity) + ','
            + '"' + frequency + '",'
            + str(report.impact) + ','
            + '"' + description + '"\n'
        )

    return csv_text


# ==================================================
# ROUTE 1: HOMEPAGE
# ==================================================

@route
def index(state: State) -> Page:
    """Displays the homepage and website navigation."""
    content = [
        Div(
            Header("Improving Our Communities, One Report at a Time", 2),
            Text(
                "A centralized platform for identifying, "
                "reporting, and prioritizing infrastructure concerns."
            ),
            Button("Submit an Infrastructure Report", "report_page"),
            style_background_color=LIGHT_BLUE,
            style_color=NAVY,
            style_padding="24px",
            style_border_radius="12px",
            style_margin="12px 0"
        ),

        create_stat_card(
            "Total Community Reports",
            str(len(state.reports))
        ),

        create_card(
            "How Civic Tracker Works",
            [
                Text("01. REPORT AN ISSUE"),
                Text(
                    "Residents submit information about infrastructure "
                    "problems in their communities."
                ),
                Text("02. ORGANIZE AND PRIORITIZE"),
                Text(
                    "Reports are ranked using severity, frequency, "
                    "community impact, and similar submissions."
                ),
                Text("03. INFORM LOCAL GOVERNMENT"),
                Text(
                    "Simplified summaries help identify common "
                    "infrastructure concerns."
                )
            ]
        ),

        create_card(
            "Explore the Website",
            [
                Button("Report an Issue", "report_page"),
                Button("Community Dashboard", "dashboard_page"),
                Button("Government Reports", "export_page"),
                Button("Learn About This Project", "about_page")
            ]
        ),

        create_card(
            "Latest Website Activity",
            [
                Text(state.status_message)
            ]
        )
    ]

    return create_page(
        state,
        "Community Overview",
        "Welcome to your community infrastructure portal.",
        content
    )


# ==================================================
# ROUTE 2: ADDITIONAL HOMEPAGE
# ==================================================

@route
def home_page(state: State) -> Page:
    """Provides an additional route to the homepage."""
    return index(state)


# ==================================================
# ROUTE 3: REPORT SUBMISSION PAGE
# ==================================================

@route
def report_page(state: State) -> Page:
    """Displays an organized infrastructure report form."""
    content = [
        create_card(
            "Before You Begin",
            [
                Text(
                    "Use this form to report an infrastructure "
                    "problem that you have noticed in your community."
                ),
                Text(
                    "Please provide as much accurate information "
                    "as possible. Your report will help organize "
                    "community concerns."
                )
            ]
        ),

        create_card(
            "01 | Identify the Problem",
            [
                Text("What type of infrastructure issue are you reporting?"),
                Text(
                    "Choose the category that best describes "
                    "the problem."
                ),
                SelectBox("issue_type", ISSUE_TYPES)
            ]
        ),

        create_card(
            "02 | Identify the Location",
            [
                Text("Where is the problem located?"),
                Text(
                    "Enter a street name, intersection, landmark, "
                    "or general area."
                ),
                TextBox(
                    "location",
                    placeholder="Example: Main Street near the library"
                )
            ]
        ),

        create_card(
            "03 | Rate the Severity",
            [
                Text("How serious is this infrastructure problem?"),
                Text("1 = Minor concern"),
                Text("2 = Slightly concerning"),
                Text("3 = Moderate concern"),
                Text("4 = Serious concern"),
                Text("5 = Very serious concern"),
                SelectBox("severity", SEVERITY_OPTIONS)
            ]
        ),

        create_card(
            "04 | Report the Frequency",
            [
                Text("How frequently does this problem occur?"),
                Text(
                    "Consider how often you notice or experience "
                    "the issue."
                ),
                SelectBox("frequency", FREQUENCY_OPTIONS)
            ]
        ),

        create_card(
            "05 | Estimate Community Impact",
            [
                Text("How much does this issue affect the community?"),
                Text("1 = Affects very few people"),
                Text("2 = Affects a small number of people"),
                Text("3 = Affects a moderate number of people"),
                Text("4 = Affects many people"),
                Text("5 = Affects a large portion of the community"),
                SelectBox("impact", IMPACT_OPTIONS)
            ]
        ),

        create_card(
            "06 | Describe the Problem",
            [
                Text(
                    "Provide additional details about what "
                    "you observed."
                ),
                Text(
                    "For example, describe the condition of the road, "
                    "the approximate size of the problem, or any "
                    "difficulties it creates."
                ),
                TextArea("description", rows=5)
            ]
        ),

        Div(
            Header("Ready to Submit?", 3),
            Text(
                "Review your information before submitting "
                "your infrastructure report."
            ),
            Button("Submit Infrastructure Report", "submit_report"),
            style_background_color=LIGHT_BLUE,
            style_color=NAVY,
            style_border_radius="12px",
            style_padding="20px",
            style_margin="12px 0"
        )
    ]

    return create_page(
        state,
        "Submit an Infrastructure Issue",
        "Help identify problems and improve your community.",
        content
    )


# ==================================================
# ROUTE 4: SUBMIT REPORT
# ==================================================

@route
def submit_report(
    state: State,
    issue_type: str,
    location: str,
    severity: int,
    frequency: str,
    impact: int,
    description: str
) -> Page:
    """Validates and saves a new infrastructure report."""
    if location.strip() == "" or description.strip() == "":
        state.status_message = (
            "Error: Please provide both a location and description."
        )

        return create_page(
            state,
            "Incomplete Report",
            "Some required information is missing.",
            [
                create_card(
                    "Missing Information",
                    [
                        Text(state.status_message),
                        Button("Return to Form", "report_page")
                    ]
                )
            ]
        )

    if issue_type not in ISSUE_TYPES:
        state.status_message = "Please select a valid issue category."

        return create_page(
            state,
            "Invalid Category",
            "Please correct your submission.",
            [
                create_card(
                    "Submission Error",
                    [
                        Text(state.status_message),
                        Button("Return to Form", "report_page")
                    ]
                )
            ]
        )

    if severity < 1 or severity > 5 or impact < 1 or impact > 5:
        state.status_message = "Please select valid ratings."

        return create_page(
            state,
            "Invalid Rating",
            "Please correct your submission.",
            [
                create_card(
                    "Submission Error",
                    [
                        Text(state.status_message),
                        Button("Return to Form", "report_page")
                    ]
                )
            ]
        )

    if frequency not in FREQUENCY_OPTIONS:
        state.status_message = "Please select a valid frequency."

        return create_page(
            state,
            "Invalid Frequency",
            "Please correct your submission.",
            [
                create_card(
                    "Submission Error",
                    [
                        Text(state.status_message),
                        Button("Return to Form", "report_page")
                    ]
                )
            ]
        )

    new_report = InfrastructureReport(
        issue_type,
        location.strip(),
        severity,
        frequency,
        impact,
        description.strip()
    )

    state.reports.append(new_report)

    state.status_message = (
        "Your infrastructure report was successfully submitted!"
    )

    return create_page(
        state,
        "Report Successfully Submitted",
        "Thank you for contributing to your community.",
        [
            create_card(
                "Submission Confirmation",
                [
                    Header("Thank You!", 2),
                    Text(state.status_message),
                    Text("Category: " + issue_type),
                    Text("Location: " + location),
                    Text("Severity: " + str(severity)),
                    Text("Community Impact: " + str(impact)),
                    Text("Frequency: " + frequency)
                ]
            ),

            create_card(
                "What's Next?",
                [
                    Text(
                        "Your report has been added to the "
                        "community dashboard."
                    ),
                    Button("View Community Dashboard", "dashboard_page"),
                    Button("Submit Another Report", "report_page")
                ]
            )
        ]
    )


# ==================================================
# ROUTE 5: COMMUNITY DASHBOARD
# ==================================================

@route
def dashboard_page(state: State) -> Page:
    """Displays ranked reports and community statistics."""
    filtered_reports = get_filtered_reports(
        state.reports,
        state.selected_category,
        state.search_location
    )

    ranked_reports = rank_reports(
        filtered_reports,
        state.sort_option
    )

    high_severity_count = 0
    total_severity = 0

    for report in state.reports:
        total_severity = total_severity + report.severity

        if report.severity >= 4:
            high_severity_count = high_severity_count + 1

    if len(state.reports) > 0:
        average_severity = round(
            total_severity / len(state.reports), 2
        )
    else:
        average_severity = 0

    content = [
        Div(
            create_stat_card(
                "Total Reports",
                str(len(state.reports))
            ),
            create_stat_card(
                "High Severity Reports",
                str(high_severity_count)
            ),
            create_stat_card(
                "Average Severity",
                str(average_severity)
            ),
            style_background_color=LIGHT_GRAY,
            style_padding="12px",
            style_border_radius="12px"
        ),

        create_card(
            "Filter Community Reports",
            [
                Text("Infrastructure Category"),
                SelectBox(
                    "category",
                    ["All Categories"] + ISSUE_TYPES,
                    state.selected_category
                ),
                Text("Search by Location"),
                TextBox("location", state.search_location),
                Text("Rank Reports By"),
                SelectBox(
                    "sort_option",
                    SORT_OPTIONS,
                    state.sort_option
                ),
                Button("Apply Filters", "filter_page")
            ]
        ),

        create_card(
            "Ranked Infrastructure Concerns",
            [
                Text(
                    "Reports are displayed from highest "
                    "to lowest priority."
                )
            ]
        )
    ]

    if len(ranked_reports) == 0:
        content.append(
            create_card(
                "No Reports Found",
                [
                    Text(
                        "There are currently no reports matching "
                        "your selected filters."
                    ),
                    Button("Submit a Report", "report_page")
                ]
            )
        )

    else:
        for index in range(len(ranked_reports)):
            report = ranked_reports[index]

            score = calculate_priority_score(
                report, state.reports
            )

            severity_level = classify_severity(report.severity)

            if severity_level == "High":
                severity_color = RED
            elif severity_level == "Moderate":
                severity_color = YELLOW
            else:
                severity_color = GREEN

            matching_count = count_similar_reports(
                report, state.reports
            )

            report_card = create_card(
                "PRIORITY RANK #" + str(index + 1),
                [
                    Header(report.issue_type, 3),
                    Text("Location: " + report.location),
                    Text("Priority Score: " + str(score)),
                    Text(
                        "Severity: " + severity_level,
                        style_color=severity_color
                    ),
                    Text("Similar Reports: " + str(matching_count)),
                    Text("Community Impact: " + str(report.impact)),
                    Button(
                        "View Report Details",
                        "details_page",
                        {
                            "report_number": state.reports.index(report)
                        }
                    )
                ]
            )

            content.append(report_card)

    content.append(
        create_card(
            "Continue Exploring",
            [
                Button("Submit an Issue", "report_page"),
                Button("Government Reports", "export_page")
            ]
        )
    )

    return create_page(
        state,
        "Community Dashboard",
        "Explore, filter, and prioritize infrastructure concerns.",
        content
    )


# ==================================================
# ROUTE 6: FILTER REPORTS
# ==================================================

@route
def filter_page(
    state: State,
    category: str,
    location: str,
    sort_option: str
) -> Page:
    """Updates dashboard filters and ranking method."""
    state.selected_category = category
    state.search_location = location
    state.sort_option = sort_option

    state.status_message = "Dashboard filters successfully updated."

    return dashboard_page(state)


# ==================================================
# ROUTE 7: REPORT DETAILS
# ==================================================

@route
def details_page(
    state: State,
    report_number: int
) -> Page:
    """Displays detailed information about one report."""
    if report_number < 0 or report_number >= len(state.reports):
        return create_page(
            state,
            "Report Not Found",
            "The requested report could not be located.",
            [
                Button("Return to Dashboard", "dashboard_page")
            ]
        )

    state.selected_report_index = report_number

    report = state.reports[report_number]

    priority_score = calculate_priority_score(
        report, state.reports
    )

    severity_level = classify_severity(report.severity)

    if severity_level == "High":
        severity_color = RED
    elif severity_level == "Moderate":
        severity_color = YELLOW
    else:
        severity_color = GREEN

    content = [
        create_card(
            "Infrastructure Report",
            [
                Header(report.issue_type, 2),
                Text("Location: " + report.location),
                Text("Description: " + report.description)
            ]
        ),

        create_card(
            "Severity and Impact Assessment",
            [
                Text(
                    "Severity Rating: " + str(report.severity),
                    style_color=severity_color
                ),
                Text("Severity Classification: " + severity_level),
                Text("Frequency: " + report.frequency),
                Text("Community Impact: " + str(report.impact))
            ]
        ),

        create_card(
            "Community Priority",
            [
                Header(str(priority_score), 2),
                Text("Calculated Priority Score"),
                Text(
                    "Similar Reports: "
                    + str(count_similar_reports(report, state.reports))
                ),
                Text(
                    "This score is an estimated ranking tool, "
                    "not an official engineering assessment."
                )
            ]
        ),

        create_card(
            "Navigation",
            [
                Button("Return to Dashboard", "dashboard_page"),
                Button("Submit Another Report", "report_page")
            ]
        )
    ]

    return create_page(
        state,
        "Infrastructure Report Details",
        "Detailed information about the selected community concern.",
        content
    )


# ==================================================
# ROUTE 8: GOVERNMENT REPORTS
# ==================================================

@route
def export_page(state: State) -> Page:
    """Creates simplified summaries for local governments."""
    content = [
        create_card(
            "Community Overview",
            [
                Header(str(len(state.reports)), 2),
                Text("Total Infrastructure Reports Submitted"),
                Text(
                    "The following information summarizes "
                    "reported community infrastructure concerns."
                )
            ]
        ),

        create_card(
            "Infrastructure Category Breakdown",
            [
                Text(
                    "Reports are grouped by category to help "
                    "identify recurring community concerns."
                )
            ]
        )
    ]

    for category in ISSUE_TYPES:
        report_count = 0
        total_severity = 0
        total_impact = 0

        for report in state.reports:
            if report.issue_type == category:
                report_count = report_count + 1
                total_severity = total_severity + report.severity
                total_impact = total_impact + report.impact

        if report_count > 0:
            average_severity = round(
                total_severity / report_count, 2
            )

            average_impact = round(
                total_impact / report_count, 2
            )

            content.append(
                create_card(
                    category,
                    [
                        Header(str(report_count), 2),
                        Text("Number of Reports"),
                        Text(
                            "Average Severity: "
                            + str(average_severity)
                        ),
                        Text(
                            "Average Community Impact: "
                            + str(average_impact)
                        )
                    ]
                )
            )

        else:
            content.append(
                create_card(
                    category,
                    [
                        Text("No reports submitted in this category.")
                    ]
                )
            )

    content.append(
        create_card(
            "CSV Data Export",
            [
                Text(
                    "The information below is formatted as CSV. "
                    "You can copy it into a spreadsheet program."
                ),
                Text(create_csv_text(state.reports))
            ]
        )
    )

    content.append(
        create_card(
            "Navigation",
            [
                Button("Return to Dashboard", "dashboard_page"),
                Button("Return Home", "index")
            ]
        )
    )

    return create_page(
        state,
        "Government Reports",
        "Simplified community infrastructure summaries.",
        content
    )


# ==================================================
# ROUTE 9: ABOUT PAGE
# ==================================================

@route
def about_page(state: State) -> Page:
    """Explains the purpose and functionality of the website."""
    content = [
        create_card(
            "Our Purpose",
            [
                Text(
                    "Civic Infrastructure Tracker is a community "
                    "reporting platform designed to help residents "
                    "identify infrastructure concerns."
                ),
                Text(
                    "The application organizes submitted reports "
                    "and ranks concerns to help highlight issues "
                    "that may deserve further attention."
                )
            ]
        ),

        create_card(
            "How the Ranking System Works",
            [
                Text("01. SEVERITY"),
                Text(
                    "Each report receives a severity rating "
                    "between 1 and 5."
                ),
                Text("02. FREQUENCY"),
                Text(
                    "Residents identify how frequently "
                    "the problem occurs."
                ),
                Text("03. COMMUNITY IMPACT"),
                Text(
                    "Residents estimate how significantly "
                    "the problem affects their community."
                ),
                Text("04. COMMUNITY SUPPORT"),
                Text(
                    "Similar reports from the same location "
                    "increase the calculated priority score."
                )
            ]
        ),

        create_card(
            "Project Information",
            [
                Text("Developed for CISC106 at the University of Delaware."),
                Text("Created using Python and the Drafter library."),
                Text(
                    "This application is an educational prototype. "
                    "Its rankings do not replace professional "
                    "engineering evaluations or government inspections."
                )
            ]
        ),

        create_card(
            "Explore Civic Tracker",
            [
                Button("Submit an Issue", "report_page"),
                Button("View Dashboard", "dashboard_page")
            ]
        )
    ]

    return create_page(
        state,
        "About Civic Infrastructure Tracker",
        "Learn more about the project and its functionality.",
        content
    )


# ==================================================
# UNIT TESTS
# ==================================================

def test_helper_functions():
    """Tests the helper functions using sample reports."""
    report_one = InfrastructureReport(
        "Pothole",
        "Main Street",
        5,
        "Often",
        4,
        "Large pothole in the road."
    )

    report_two = InfrastructureReport(
        "Pothole",
        "Main Street",
        3,
        "Sometimes",
        3,
        "Another pothole."
    )

    reports = [report_one, report_two]

    assert_equal(classify_severity(5), "High")
    assert_equal(classify_severity(3), "Moderate")
    assert_equal(classify_severity(1), "Low")

    assert_equal(get_frequency_score("Constantly"), 4)
    assert_equal(get_frequency_score("Rarely"), 1)

    assert_equal(count_similar_reports(report_one, reports), 2)

    # The correct expected priority score is 21.
    assert_equal(
        calculate_priority_score(report_one, reports),
        21
    )

    assert_equal(
        len(get_filtered_reports(reports, "Pothole", "")),
        2
    )

    assert_equal(
        len(get_filtered_reports(reports, "Road Damage", "")),
        0
    )

    assert_equal(
        len(rank_reports(reports, "Overall Priority")),
        2
    )

    assert_equal(
        create_csv_text(reports).startswith(
            "Issue Type,Location"
        ),
        True
    )


def test_routes():
    """Tests that website routes return Drafter pages."""
    test_state = State()

    sample_report = InfrastructureReport(
        "Pothole",
        "Main Street",
        5,
        "Often",
        4,
        "Large pothole in the road."
    )

    test_state.reports.append(sample_report)

    assert_equal(isinstance(index(test_state), Page), True)
    assert_equal(isinstance(home_page(test_state), Page), True)
    assert_equal(isinstance(report_page(test_state), Page), True)
    assert_equal(isinstance(dashboard_page(test_state), Page), True)

    assert_equal(
        isinstance(
            filter_page(
                test_state,
                "Pothole",
                "",
                "Overall Priority"
            ),
            Page
        ),
        True
    )

    assert_equal(
        isinstance(details_page(test_state, 0), Page),
        True
    )

    assert_equal(isinstance(export_page(test_state), Page), True)
    assert_equal(isinstance(about_page(test_state), Page), True)

    # Test valid report submission.
    submission_state = State()

    submit_report(
        submission_state,
        "Road Damage",
        "Main Street",
        4,
        "Often",
        5,
        "Damaged road surface."
    )

    assert_equal(len(submission_state.reports), 1)

    # Test invalid report submission.
    invalid_state = State()

    submit_report(
        invalid_state,
        "Road Damage",
        "",
        4,
        "Often",
        5,
        "Damaged road surface."
    )

    assert_equal(len(invalid_state.reports), 0)


# ==================================================
# WEBSITE STARTUP
# ==================================================

test_helper_functions()
test_routes()

set_website_title("Civic Infrastructure Tracker")

set_site_information(
    "Your Name",
    "A community infrastructure reporting and "
    "prioritization application.",
    "No external sources used.",
    "See the CISC106 final project planning document "
    "in the GitHub repository.",
    []
)

start_server(State())


