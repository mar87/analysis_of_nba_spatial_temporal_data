#loading the required packages
library(shiny); library(shinydashboard)

#establishing the dashboard
dashboardPage(
  dashboardHeader(title = "Shot Locations"),
  dashboardSidebar(
    #widgets to select the values of variables to filter on 
    sliderInput("shooter_vel", "Shooter Velocity (ft/sec)",0, 12, c(0,12), step=0.1),
    sliderInput("shooter_dist", "Shooter Distance Traveled",0, 170, c(0,170), step=0.5),
    sliderInput("def_dist", "Defender Distance",0, 40, c(0,40), step=0.1),
    sliderInput("defender_angle", "Defender Angle", -180, 180, c(-180,180), step=0.5),
    sliderInput("close_def", "Number of Close Defenders", 0, 5, c(0, 5), step = 1),
    sliderInput("team_dist", "Teammate Distance", 0, 65, c(0, 65), step =0.1),
    sidebarMenu(
      menuItem("All Shots", tabName = "all_shots"),
      menuItem("Project Description", tabName = "desc")
    )
  ),
  dashboardBody(
    tabItems(
      tabItem("all_shots", 
          #outputting the plot from the server file
          plotOutput('P1')
      ), 
      tabItem("desc", 
          #project description and links to GitHub
          h4("This application allows the user view shots from a handful of games during the 2015-2016 NBA season.
                The variables on the left were used to fit classification models to determine if a shot was made or missed and were generated using 
                the tracking data from NBA games. The application is part of Megan Robertson's thesis submitted for
                her Master of Statistical Science degree from Duke University. For more details on the project and to see the final report see: http://megrobertson.weebly.com/an_analysis_of_nba_spatio_temporal_data"),
          h4("Variable Key:"),
          h4("Shooter Velocity: Speed of shooter at the time of shot"),
          h4("Shooter Distance Traveled: Distance traveled by shooter ten seconds before shot"),
          h4("Defender Distance: Distance between shooter and closest defender"),
          h4("Defender Angle: Angle between shooter and closest defedner"),
          h4("Number of Close Defenders: Number of defenders within five feet"),
          h4("Teammate Distance: Distance to the closest teammate")
          )
  )
)
)
