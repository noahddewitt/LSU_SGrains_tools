library(shiny)
library(DT)

library(DBI)
library(RSQLite)

library(tidyverse)
library(ggplot2)

##Okay, here's where I access the django model. I'll have to mess with this in production

#Debug
#if (!interactive()) sink(stderr(), type = "output")

djangoRoot <- "/data/sg_db/LSU_SGrains_tools/sg_db/"

##############Shiny application ################


getCrossInfo <- function(lineMat, wcpInfo, crossesMade) {
  #Remember that eventually crossesMade should be much larger than lineMat
  #Two directions cross can go
  madeCombos <- unique(rbind(cbind(crossesMade$parent_one_id, crossesMade$parent_two_id), 
                             cbind(crossesMade$parent_two_id, crossesMade$parent_one_id)))
  
  wcpNames <- wcpInfo$desig_text
  names(wcpNames) <- wcpInfo$wcp_id
  
  idLineMat <- lineMat[, c(1:2)]
  idLineMat$P1 <- names(wcpNames)[match(idLineMat$P1, wcpNames)]
  idLineMat$P2 <- names(wcpNames)[match(idLineMat$P2, wcpNames)]
  #potCombos <- unique(rbind(cbind(lineMat$P1, lineMat$P2), cbind(lineMat$P2, lineMat$P1)))
  
  lineMat$Status <- as.character(paste0(idLineMat$P1, idLineMat$P2) %in% paste0(madeCombos[,1], madeCombos[,2]))
  
  #Unless I *Really* messed something up, the original lineMat should be same order as original.
  for (i in c(1:nrow(lineMat))) {
    #Check for cross status
    if (lineMat$Status[i] == "FALSE") {
      lineMat$Status[i] <- ""
    } else {
      crossInfo <- crossesMade[crossesMade$parent_one_id == idLineMat$P1[i] & crossesMade$parent_two_id == idLineMat$P2[i],]
      if (nrow(crossInfo) == 0) {
        crossInfo <- crossesMade[crossesMade$parent_one_id == idLineMat$P2[i] & crossesMade$parent_two_id == idLineMat$P1[i],]
      }
      lineMat$Status[i] <- crossInfo$status_text
    }
    #Check for group conflict
    p1Info <- wcpInfo[wcpInfo$wcp_id == idLineMat$P1[i], ]$cp_group_text
    p2Info <- wcpInfo[wcpInfo$wcp_id == idLineMat$P2[i], ]$cp_group_text
    if (((p1Info == "G") & (p2Info != "A")) | ((p2Info == "G") & (p1Info != "A"))) {
      lineMat$UC[i] <- -1
    }
  }
  return(lineMat)
}

crossesMadePlot <- function(wcpInfo, crossesMade) {
  #For now, we want to exclude topcrosses
  wcpInfo <- wcpInfo[wcpInfo$cp_group_text != "T", ]
  
  #Grid of all possible combinations.
  
  wcpInfoGrid <- data.frame()
  
  for (wcp_id_p1 in c(1:nrow(wcpInfo))) {
    for (wcp_id_p2 in c(1:nrow(wcpInfo))) {
      p1_id = wcpInfo$wcp_id[wcp_id_p1]
      p2_id = wcpInfo$wcp_id[wcp_id_p2]
      
      p1_desig = wcpInfo$desig_text[wcp_id_p1]
      p2_desig = wcpInfo$desig_text[wcp_id_p2]
      
      crossInfo <- crossesMade[crossesMade$parent_one_id == p1_id & 
                               crossesMade$parent_two_id == p2_id, ]
      
      if (nrow(crossInfo) == 0) {
        crossInfo <- crossesMade[crossesMade$parent_one_id == p2_id & 
                                 crossesMade$parent_two_id == p1_id, ]
      }
      
      if (nrow(crossInfo) > 0) {
        cross_status = crossInfo$status_text
      } else {
        if(p1_id == p2_id) {
          cross_status = "Self"
        } else {
          cross_status = "Unmade"
        }
      }
      
      wcpInfoGrid <- rbind(wcpInfoGrid, c(P1 = p1_desig,
                                        P2 = p2_desig,
                                        St = cross_status))
    }
  }
  
  colnames(wcpInfoGrid) <- c("P1", "P2", "St")
  
  wcpInfoGrid$P1 <- factor(wcpInfoGrid$P1, levels = c(unique(wcpInfoGrid$P1)))
  wcpInfoGrid$P2 <- factor(wcpInfoGrid$P2, levels = c(rev(unique(wcpInfoGrid$P2))))
  
  
  ggplot(wcpInfoGrid, aes(x = P1, y = P2, fill = St)) + 
    geom_tile(color = "grey") +
    scale_fill_manual(values = c("Self" = "#3C1053",
                                  "Made"="#D29F13",
                                "Set"="#0B5D1E",
                                "Failed"="#A44A3F",
                                "Unmade" = "#F1EEDB")) +
  #  theme_minimal() +
    xlab("") + ylab("") +
    theme(plot.background = element_rect(fill = "#F1EEDB", color = NA),
          panel.grid.major = element_blank(),
          panel.grid.minor = element_blank(),
          panel.border = element_rect(colour = "darkgrey", fill=NA, size=1.5),
          axis.text.y = element_text(size = rel(1.4), face = "bold"),
          axis.text.x = element_text(size=rel(1.4), face = "bold", angle = 45, hjust=1),
          legend.position = "none")
}



server <- function(input, output, session) {
  
  sgDB <- dbConnect(RSQLite::SQLite(), paste0(djangoRoot, "db.sqlite3"))
  wcp_Entries <- dbGetQuery(sgDB, "SELECT * FROM crossing_wcp_entries")

  #Get already-made crosses (crosses "in progress", aka targets, plus lines confirmed.)
  wcp_Xs <- dbGetQuery(sgDB, "SELECT * FROM crossing_crosses")

  dbDisconnect(sgDB)

  #Get matrix of available lines, also send info on already made crosses.
  output$xingPlot = renderPlot({crossesMadePlot(wcp_Entries, wcp_Xs)}, 
                               width = 880, height = 780)
 
}

ui <- fluidPage(
 # titlePanel("Cross Information",windowTitle = "Crossing"),
  tags$style('.container-fluid {
                             background-color: #F1EEDB;
              }
             body {overflow-y: hidden;}'),  #Hack to disable scroll bar
  fluidRow(
    column(12, style = "height: 100vh;",
      plotOutput('xingPlot', click = "heatmap_click")
    )
  )
)

shinyApp(ui = ui, server = server)
