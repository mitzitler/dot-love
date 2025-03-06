import { useState, useRef, useEffect } from "react";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";
import { Tooltip, withTooltip } from "react-tippy";
import 'react-tippy/dist/tippy.css'

export function RegistryPageChart({Data, displayedId, setDisplayedId}) {
    //const [activeGift, setActiveGift] = useState(null)
    //const [tooltipData, setTooltipData] = useState(null)
    // const [selectedId, setSelectedId] = useState(null)
    const chartRef = useRef();
    // const tooltipRef = useRef(null);

    // function handleActiveGift(giftInput) {
    // //    giftRef.current.focus()
    //     setActiveGift(giftInput)
    //    console.log("function says active gift id is " + giftInput)
    // }

    // trying this: https://ncoughlin.com/posts/d3-react#data-and-accessors-as-props
    // also looking at: https://stackoverflow.com/questions/29164092/on-click-display-other-data-in-separate-div-in-d3-js-passing-by-value
    // this worked: https://www.griddynamics.com/blog/using-d3-js-with-react-js
    useEffect(() => {
        // if (Data && chartRef.current) {
            const dataset = Data
            const svgGiftRef = d3.select(chartRef.current)
            svgGiftRef.selectAll("*").remove()

            let dimensions = {
                w: 450,
                h: 450,
                margins: 50
            };

            let tooltip = d3
                .select("body")
                .append("div")
                .style("position", "absolute")
                .style("line-height", 1.1)
                .style("border-radius", "0.4em")
                .style("box-shadow", "0em 0em .5em rgb(165, 163, 163)")
                .style("font-size", "10px") 
                .style("text-align", "center")
                .style("width", "50px") 
                .style("height", "40px") 
                .style("background", "white")
                .style("color", "#9cb3c3")
                .style("top", 0)
                .style("left", 0)
                .style("display", "none")

            const width = dimensions.w - (dimensions.margins * 1.5);
            const height = dimensions.h - (dimensions.margins * 1.5);

            const svg2 = svgGiftRef.append("g")
                .attr("tranform","translate("+dimensions.margins+","+dimensions.margins+")")

        //    const tooltip = d3.select(tooltipRef.current);
            
            const yScale = d3
                .scaleLinear()
                .domain([-10, 10])
                .range([height, dimensions.margins])
                .nice()
            const xScale = d3 
                .scaleLinear()
                .domain([-10, 10])
                .range([dimensions.margins, width])
                .nice()
            const allGroups = dataset.map((d) => String(d.price_cat));
            const colorScale = d3
                  .scaleOrdinal()
                  .domain(allGroups)
                  .range(["#32a852", "#e052eb", "#5eb4ff", "#8037b8", "#e35954"]);
              
            
            const xAxis = d3 
                .axisBottom(xScale)
                .ticks(10)
                .tickSize(-(height- (dimensions.margins*0.66)))
            const xAxisGroup = svg2.append("g")
                .attr("transform", `translate(0, ${height+(dimensions.margins/3)})`)
                .call(xAxis);
            xAxisGroup.select(".domain").remove();
            xAxisGroup.selectAll("line").attr("stroke", "rgba(255, 255, 255, 0.2)");
            xAxisGroup.selectAll("text")
                .attr("opacity", 0.5)
                .attr("color", "#782614")
                .attr("font-size", "0.75rem")

            const yAxis = d3 
                .axisLeft(yScale)
                .ticks(10)
                .tickSize(-(width-(dimensions.margins*0.66)))
            const yAxisGroup = svg2.append("g")
                .attr("transform","translate("+dimensions.margins*0.7+")")
                .call(yAxis);
            yAxisGroup.select(".domain").remove();
            yAxisGroup.selectAll("line").attr("stroke", "rgba(255, 255, 255, 0.2)");
            yAxisGroup.selectAll("text")
                .attr("opacity", 0.5)
                .attr("color", "#782614")
                .attr("font-size", "0.75rem")
            
            // i could make this var reusable as long as ticks(1) can be an arg passed later
            const xAxisZero = d3 
                .axisBottom(xScale)
                .ticks(1)
                .tickSize(-(height- (dimensions.margins*0.66)))
            const xAxisZeroGroup = svg2.append("g")
                .attr("transform", `translate(0, ${height+(dimensions.margins/3)})`)
                .call(xAxisZero);
            xAxisZeroGroup.select(".domain").remove();
            xAxisZeroGroup.selectAll("line").attr("stroke", "#782614");
            xAxisZeroGroup.selectAll("text")
                .attr("opacity", 0)

            const yAxisZero = d3 
                .axisLeft(yScale)
                .ticks(1)
                .tickSize(-(width-(dimensions.margins*0.66)))
            const yAxisZeroGroup = svg2.append("g")
                .attr("transform","translate("+dimensions.margins*0.7+")")
                .call(yAxisZero);
            yAxisZeroGroup.select(".domain").remove();
            yAxisZeroGroup.selectAll("line").attr("stroke", "#782614");
            yAxisZeroGroup.selectAll("text")
                .attr("opacity", 0)

            svg2.append("text")
                .attr("text-anchor", "end")
                .attr("x", width-dimensions.margins)
                .attr("y", height+dimensions.margins)
                .attr("stroke", "#782614")
                .text("Size Score: smallest to largest");
            
            svg2.append("text")
                .attr("text-anchor", "end")
                .attr("transform", "rotate(-90)")
                .attr("x", -(dimensions.margins/2))
                .attr("y", dimensions.margins/4)
                .attr("stroke", "#782614")
                .attr("text-size", "0.5rem")
                .text("Function Score: most practical to most artsy");

            svg2
                .selectAll("circle")
                .data(dataset)
                .enter()
                .append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .attr("r", 5)
                .attr("fill", d => colorScale(d.price_cat))
                .attr("stroke", d => colorScale(d.price_cat))
                .attr("fill-opacity", 0.5)
                .on("mouseover", (mouseEvent, d) => {
                    d3.select(mouseEvent.target).transition().attr("r", 8)
                    tooltip.transition().duration(0).style("display", "block")
                    tooltip
                        .style("display", "block")
                        .html(`<div><span>My name is ${d.name}</span></div>`)
                        .style("left", (mouseEvent.pageX + 5) + "px")
                        .style("top", (mouseEvent.pageY - 24) + "px")
                    const [x,y] = d3.pointer(mouseEvent);
                    const dataset = d
                    console.log("i am recognizing gift id " + dataset.id)
                    // setTooltipData({x, y, dataset: d})
                    console.log(`<div><span>${d.name}</span></div>`)
                    console.log(mouseEvent.x, mouseEvent.y)
                })
                .on("mouseout", (mouseEvent) => {
                    // setTooltipData(null)
                    d3.select(mouseEvent.target).transition().attr("r", 5)
                    tooltip.transition().duration(0)
                    tooltip 
                        .style("left", "0px")
                        .style("top", "0px")
                        .style("display", "none")
                })
                .on("mousedown", (mouseEvent, d) => {
                    const [x,y] = d3.pointer(mouseEvent);
                    const dataset = d
                    setDisplayedId(d.id)
                    console.log("gift id is " + dataset.id + 
                               " and my index is " + dataset.index +
                                " and name is " + dataset.name)
                })

        // }      
    }, [Data, setDisplayedId])
    console.log(displayedId)
    return (
        <div>
            {/* tooltip looks very bad with this whole set up */}
            {/* <Tooltip title="hello world" position="bottom" trigger="click">
            </Tooltip> */}
            {/* <svg ref={chartRef} width={500} height={500}> */}
            <svg ref={chartRef} width={400} height={450}> {/* need more css here */}
            </svg>
        </div>
    )
}