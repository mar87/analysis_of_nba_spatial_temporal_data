library(shiny); library(dplyr); library(ggvis); library(mosaic); library(data.table); library(shinydashboard);library(png)
library(ggplot2); library(grid); library(jpeg)
#change working directory to where data is stored
data <-  data.frame(fread("shot_model_data.csv"))
data$made = as.factor(data$made)
court_image = readJPEG("Court_image.jpeg")

shinyServer(function(input, output){
  
  plotData <- reactive({ 
    min_shoot_vel = input$shooter_vel[1]
    max_shoot_vel = input$shooter_vel[2]
    min_shoot_dist = input$shooter_dist[1]
    max_shoot_dist = input$shooter_dist[2]
    min_def_dist = input$def_dist[1]
    max_def_dist = input$def_dist[2]
    min_def_ang = input$defender_angle[1]
    max_def_ang = input$defender_angle[2]
    min_team_dist = input$team_dist[1]
    max_team_dist = input$team_dist[2]
    min_num_def = input$close_def[1]
    max_num_def = input$close_def[2]

    player = input$player
    
    df <- data %>%
      filter(shooter_vel_at_shot <= max_shoot_vel & shooter_vel_at_shot >= min_shoot_vel) %>%
      filter(closest_defender_dist <= max_def_dist & closest_defender_dist >= min_def_dist) %>%
      filter(closest_defender_angle <= max_def_ang & closest_defender_angle >= min_def_ang) %>%
      filter(closest_teammate_dist <= max_team_dist & closest_teammate_dist >= min_team_dist) %>%
      filter(num_close_def <= max_num_def & num_close_def >= min_num_def) %>%
      filter(shooter_dist_traveled <= max_shoot_dist & shooter_dist_traveled >= min_shoot_dist)
    })
  
  output$plot <- renderPlot(xyplot(y_loc ~ x_loc, group = made, data=plotData(),auto.key=list(space='top', columns=2, lines=TRUE, points=FALSE, panel=function(x,y){
    panel.xyplot(x,y)
    panel.abline(h=0, col='red')
                        }))
                            )

  #ggplot
  output$P1 <- renderPlot({
    ggplot(plotData(), aes_string(x = 'x_loc', y='y_loc', color='made')) + annotation_custom(rasterGrob(court_image, width=unit(1,"npc"), height=c(0.05,1.07)), -Inf, Inf, -Inf, Inf) + geom_point() +xlim(-4, 96) + ylim(0, 50) + theme(axis.title.x=element_blank(),axis.text.x=element_blank(),axis.ticks.x=element_blank(),axis.title.y=element_blank(),axis.text.y=element_blank(),axis.ticks.y=element_blank())+ labs(color = "Shot Outcome\n") + scale_color_manual(labels = c("Made", "Missed"), values = c("steelblue1", "indianred1"))}, width = 1000, height = 500)
}
)