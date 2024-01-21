library(shiny)
library(DT)

library(DBI)
library(RSQLite)

library(tidyverse)
library(readxl)
library(ggplot2)
library(ggnewscale)

#Debug
if (!interactive()) sink(stderr(), type = "output")

djangoRoot <- "/data/sg_db/LSU_SGrains_tools/sg_db/"

##############Shiny application ################

#Render crossing matrix plot using available fmles

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
  
  lineMat$Status <- as.character(paste0(idLineMat$P1, idLineMat$P2) %in% paste0(madeCombos[,1], madeCombos[,2]))
  
  #Unless I *Really* messed something up, the original lineMat should be same order as original.
  for (i in c(1:nrow(lineMat))) {
    #Check for cross status
    if (lineMat$Status[i] == "FALSE") {
      lineMat$Status[i] <- "Unmade"
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

crossingPlot <- function(lineMat, wcpInfo, crossesMade) {
  if (nrow(lineMat) > 0) {
    lineMat <- getCrossInfo(lineMat, wcpInfo, crossesMade)
    lineMat$Status <- as.factor(lineMat$Status)

  } else {
    #Otherwise throws error
    lineMat[1, ] <- NA
    lineMat$Status <- NA
    lineMat <- lineMat[-1, ]
  }
  
  print(lineMat)
  #Get info for lines with zero
  crossPlot <- ggplot(lineMat, aes(x = as.factor(P1), y = as.factor(P2), fill = UC)) + 
  geom_tile(color = "black", show.legend = F) +
  xlab("Available Females") +
  ylab("Available Males") +
  scale_fill_gradient2(low = "#8F3418", mid = "#FFFFFF", high = "#3C1053", na.value = "#FFFFFF", limits = c(-2, 3)) + #May have to adjust limits, prevent color shifts as lines added/removed
  theme_minimal() +
  theme(plot.background = element_rect(fill = "#F1EEDB", color = NA),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.x = element_text(angle = 90, vjust = 0.5))
  
  crossPlot + 
    ggnewscale::new_scale_fill() +
    geom_tile(aes(fill = Status, width = 0.75, height = 0.4)) +
    scale_fill_manual(values = c("Made"= alpha(c("#D29F13"), 0.6),"Set"= alpha(c("#0B5D1E"), 0.6), 
                                 "Failed"= alpha(c("#A44A3F"), 0.6), "Unmade" = alpha(c("#FFFFFF"), 0))) +
    theme(legend.position="none")
}


getAvailMat <- function(aFmles, aMales, priorMat) {
  availablePriorMat <- priorMat[priorMat[,1] %in% aFmles, ]
  availablePriorMat <- availablePriorMat[availablePriorMat[,2] %in% aMales, ]
  
  return(availablePriorMat)
}

#Code for DT buttons taken from https://gist.github.com/thisisnic/11d6b02007921b1ae872167049a83974
shinyInput <- function(FUN, n, id, ...) {
  #For each of n, create a new input using the FUN function and convert to character
  vapply(seq_len(n), function(i){
    as.character(FUN(paste0(id, i), ...))
  }, character(1))
  
}

#Code for generating increment up/down buttons for datatables
incButton <- function(nRow, mOrF, pOrM) {
  if(pOrM == "minus") {
    butSym <- "-"
  } else if (pOrM == "plus") {
    butSym <- "+"
  }
 
  #This is a little hacky -- in the case that we are doing the cross table,
  #We only want ONE button. If you end up making more tables, edit this code.
  if (grepl("@", nRow)) {
	as.character(
		     actionButton(paste0(mOrF, '_', pOrM, '_button_', nRow),
		     label = butSym,
		     onclick = 'Shiny.setInputValue(\"select_button\", this.id, {priority: \"event\"})'
	))

  } else {
  	shinyInput(
    	FUN = actionButton,
    	n = nRow,
    	id = paste0(mOrF, '_', pOrM, '_button_'),
    	label = butSym,
    	onclick = 'Shiny.setInputValue(\"select_button\", this.id, {priority: \"event\"})'
  )
  }

}

#This only goes up to five. I think if it's past that then this view won't bee too useful :)
getPurdyDelim <- function(p1Str, p2Str) {
	if (grepl("\\/4\\/", p1Str) | grepl("\\/4\\/", p2Str)) {
		delim <- " /5/ "	
	} else if (grepl("\\/3\\/", p1Str) | grepl("\\/3\\/", p2Str)) {
		delim <- " /4/ "	
	} else if (grepl("\\/\\/", p1Str) | grepl("\\/\\/", p2Str)) {
		delim <- " /3/ "	
	} else {
		delim <- " // "	
	} 
	return(delim)
}

server <- function(input, output, session) {
  
  sgDB <- dbConnect(RSQLite::SQLite(), paste0(djangoRoot, "db.sqlite3"))
  wcp_Entries <- dbGetQuery(sgDB, "SELECT * FROM crossing_wcp_entries")

  #Get already-made crosses (crosses "in progress", aka targets, plus lines confirmed.)
  wcp_Xs <- dbGetQuery(sgDB, "SELECT * FROM crossing_crosses")

  dbDisconnect(sgDB)

  tryPriorMat <- try(read.csv("wcp24_allCrossPreds.csv") )

  if (class(tryPriorMat) != "try-error") {
	longPriorMat <- read.csv("wcp24_allCrossPreds.csv")
	longPriorMat$P1 <- as.character(longPriorMat$P1)
	longPriorMat$P2 <- as.character(longPriorMat$P2)
  } else {
  	longPriorMat <- data.frame() 
  }
  #This and related code prevents jumping back to first page on update
  lines_pg <- reactiveVal(1)
  
  availableLines <- reactiveValues(
    fmles = c(),
    males = c()
  )
  
  
  lineDF <- data.frame(Desig = wcp_Entries$desig_text, 
                       fs = 0, ms = 0)
  
  allLines <-  
    reactiveValues(lineDF_Buttons = cbind(Desig = lineDF$Desig, 
                             fM = incButton(nrow(lineDF), "f", "minus"),
                             fs = lineDF$ms,
                             fP = incButton(nrow(lineDF), "f", "plus"),
                             mM = incButton(nrow(lineDF), "m", "minus"),
                             ms = lineDF$fs,
                             mP = incButton(nrow(lineDF), "m", "plus")
      ))
 
  #Initialize empty, will fill via clicking on heatmap 
  allXs <- reactiveValues(crossDF_Buttons = data.frame(Female = as.character(), Male = as.character(), Ped = as.character(), Genes = as.character(), k = as.character(), indx = as.numeric(), xM = as.numeric()))
	
  observe({
      if (!is.null(input$upload)) { 
      	file.copy(input$upload$datapath,
                "wcp24_allCrossPreds.csv", overwrite = TRUE)
      	session$reload()
      }
   })
  #Adjust availability of male/female parents based on table button press 
  observeEvent(input$select_button, {
    # take the value of input$select_button, e.g. "button_1"
    # get the parent type (m/f), plus or minus, row number
    selButtonInfo <- strsplit(input$select_button, split = "_")[[1]]
    
    lines_pg(input$lineData_rows_current[1])
    
    if (selButtonInfo[2] == "plus") {
      incVal <- 1
    } else {
      incVal <- -1
    }

    #If this is in the allLines table, it's a real row. Otherwise, it's an id.     
    btnRow <- selButtonInfo[4]
    if (!grepl("@", btnRow)) {btnRow <- as.numeric(btnRow)}  

    tempAllLines <- data.frame(isolate(allLines$lineDF_Buttons))
    
    if (selButtonInfo[1] == "f") {
      
      allLines$lineDF_Buttons[btnRow, 3] <- as.character(as.numeric(tempAllLines$fs[btnRow]) + incVal)
      
      #Update plot of crosses given new fmles lines
      availableLines$fmles <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 3]) > 0), 1]
      availableLines$fmles <- availableLines$fmles[order(availableLines$fmles)]
      
    } else if (selButtonInfo[1] == "m") {
      
      allLines$lineDF_Buttons[btnRow, 6] <- as.character(as.numeric(tempAllLines$ms[btnRow]) + incVal)
      
      #Update plot of crosses given new males lines
      availableLines$males <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 6]) > 0), 1]
      availableLines$males <- availableLines$males[order(availableLines$males)]
      
    } else if (selButtonInfo[1] == "x") {
      #This will be a button in the cross table. We remove lines from the "crossing" allocation
      #And move them back into the available lines for fmles and fefmles for crossing
      #Here's the pain -- have to operate on cross id instead of row
      #(I think hypothetically I now can't make two of the same cross, but that's good)
      fEno <- gsub("^F1", "F1_", gsub("@.*", "", btnRow)) 
      mEno <- gsub("^F1", "F1_", gsub(".*@", "", btnRow))

      tempAllXs <- data.frame(isolate(allXs$crossDF_Buttons))
      
      #Remove row from table. Data.frame keeps it from turning into a vector when nrow = 1
      crossMatch <- which(grepl(paste0(fEno, "\\: "), tempAllXs[,1]) & 
			  grepl(paste0(mEno, "\\: "), tempAllXs[,2]))

      allXs$crossDF_Buttons <- data.frame(allXs$crossDF_Buttons[-crossMatch, ])


      #The button position is now relative to the cross table, not the allLines table.
      fmleRow <- which(tempAllLines[,1] == gsub("^.*\\: ", "", tempAllXs[[crossMatch, 1]]))
      maleRow <- which(tempAllLines[,1] == gsub("^.*\\: ", "", tempAllXs[[crossMatch, 2]]))
      
      #Return fmle parent
      allLines$lineDF_Buttons[fmleRow, 3] <- as.character(as.numeric(tempAllLines$fs[fmleRow]) + 1)
      availableLines$fmles <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 3]) > 0), 1]
      availableLines$fmles <- availableLines$fmles[order(availableLines$fmles)]

      #Return male parent
      allLines$lineDF_Buttons[maleRow, 6] <- as.character(as.numeric(tempAllLines$ms[maleRow]) + 1)
      availableLines$males <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 6]) > 0), 1]
      availableLines$males <- availableLines$males[order(availableLines$males)]
      
    } else {
      print("Unexpected button label!")
    }
  })
  
  observeEvent(input$heatmap_click, {
    if (length(availableLines$fmles) > 0 & length(availableLines$males) > 0) {
    #Convert x/y coord from plot click into line name
    xName <- availableLines$fmles[[round(as.numeric(input$heatmap_click$x))]]
    yName <- availableLines$males[[round(as.numeric(input$heatmap_click$y))]]

    crossK <- longPriorMat[(longPriorMat$P1 == xName) & (longPriorMat$P2 == yName), ]$K
    crossK <- round(crossK, 2)

    crossFIndx <- longPriorMat[(longPriorMat$P1 == xName) & (longPriorMat$P2 == yName), ]$fhbIndex
    crossFIndx <- round(crossFIndx, 2)

    crossIndx <- longPriorMat[(longPriorMat$P1 == xName) & (longPriorMat$P2 == yName), ]$selIndex
    crossIndx <- round(crossIndx, 2)

    fEno <- wcp_Entries[wcp_Entries$desig_text == xName, ]$eno_int
    mEno <- wcp_Entries[wcp_Entries$desig_text == yName, ]$eno_int

    xId <- gsub("_", "", paste0(fEno, "@", mEno))

    fGenes <- wcp_Entries[wcp_Entries$desig_text == xName, ]$genes_text
    mGenes <- wcp_Entries[wcp_Entries$desig_text == yName, ]$genes_text

    fPed <- wcp_Entries[wcp_Entries$desig_text == xName, ]$purdy_text
    mPed <- wcp_Entries[wcp_Entries$desig_text == yName, ]$purdy_text


    #Create new cross entry in "holding" table
    newCross <-  cbind(Female = paste0(fEno, ": ", xName),
                       Male = paste0(mEno, ": ", yName),
		       Ped = paste0(fPed, getPurdyDelim(fPed, mPed), mPed),
		       Genes = paste0(fGenes, " / ", mGenes),
		       k = as.numeric(crossK),
		       fIndx = as.numeric(crossFIndx),
		       indx = as.numeric(crossIndx),
                       xM = incButton(xId, "x", "minus"))
   
    allXs$crossDF_Buttons <- rbind(newCross, allXs$crossDF_Buttons)
    
    #We've "budgeted" for the fmle and fefmle, so now we have to remove them from the counts
    tempAllLines <- data.frame(isolate(allLines$lineDF_Buttons))
    
    #Figure out where we are within the allLines DF
    xCoord <- which(tempAllLines[,1] == xName)
    yCoord <- which(tempAllLines[,1] == yName)
    
    #Update fmle data to remove chosen fmle
    allLines$lineDF_Buttons[xCoord, 3] <- as.character(as.numeric(tempAllLines$fs[xCoord]) - 1)
    availableLines$fmles <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 3]) > 0), 1]
    #Since we're re-drawing from the separate directory, have to re-order
    availableLines$fmles <- availableLines$fmles[order(availableLines$fmles)]
    
    #Update fefmle data to remove chosen fefmle
    allLines$lineDF_Buttons[yCoord, 6] <- as.character(as.numeric(tempAllLines$ms[yCoord]) - 1)
    availableLines$males <- allLines$lineDF_Buttons[which(as.numeric(allLines$lineDF_Buttons[, 6]) > 0), 1]
    availableLines$males <- availableLines$males[order(availableLines$males)]
    
    }
    }
  )
  
  output$lineData = renderDT(
    {allLines$lineDF_Buttons},
    escape = FALSE, selection = 'none',
    options = list(
      #Javascript starts index at 0
      scrollY = '300px', paging = TRUE, displayStart = lines_pg() - 1,
      iDisplayLength = 5,
      autoWidth = FALSE,
      columnDefs = list(
        list(width = '500px', targets = c(0)),
        list(className = 'dt-center', width = '20px', targets = c(2, 5)),
        list(className = 'dt-center', width = '10px', targets = c(1, 3, 4, 6)))
    ) 
  ) 
  
  #Get matrix of available lines, also send info on already made crosses.
  output$xingPlot = renderPlot({crossingPlot(getAvailMat(
    aFmles = availableLines$fmles,
    aMales = availableLines$males,
    priorMat = longPriorMat
  ), wcp_Entries, wcp_Xs)})
 
  
  output$crossData = renderDT(
    {allXs$crossDF_Buttons},
    escape = FALSE, selection = 'none', rownames = FALSE,
    option = list(
      scrollY = '300px', paging = FALSE
    )
  )
}

ui <- fluidPage(
  titlePanel("Cross Information",windowTitle = "Crossing"),
  tags$style('.container-fluid {
                             background-color: #F1EEDB;
              }'), 
  fluidRow(
    column(5, 
      DTOutput('lineData')
    ),
    
    column(7,
      fileInput('upload', "Upload Cross Predictions:", accept = c(".csv")),
      plotOutput('xingPlot', click = "heatmap_click")
    )
  ),

  fluidRow(
	column(12, DTOutput('crossData'))
  )
)

shinyApp(ui = ui, server = server)
