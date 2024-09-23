import { useState, useRef, useEffect } from "react";
import * as d3 from "d3";
import { scaleLinear } from "d3-scale";
import { Tooltip, withTooltip } from "react-tippy";
import 'react-tippy/dist/tippy.css'

// figure out useSpring from "react-spring"

// const Data = [
//     { x: 1,   y: 2,   id: 1, name: "Teapot"  },
//     { x: 2,   y: 3,   id: 2, name: "Toaster" },
//     { x: 3,   y: 5,   id: 3, name: "Towels" },
//     { x: 4,   y: 4,   id: 4, name: "Painting" },
//     { x: 5,   y: 7,   id: 5, name: "Cups" },
//     { x: -10, y: 10,  id: 6, name: "Forks" },
//     { x: 10,  y: 10,  id: 7, name: "Wine" },
//     { x: -10, y: -10, id: 8, name: "Table" },
//     { x: 10,  y: -10, id: 9, name: "Toy" },
// ]


export function RegistryChartD3({Data, displayedId, setDisplayedId}) {
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
                w: 500,
                h: 500,
                margins: 60
            };

            let tooltip = d3
                .select("body")
                .append("div")
                .style("position", "absolute")
                .style("line-height", 1.1)
                .style("border-radius", "0.4em")
                .style("box-shadow", "0em 0em .5em rgb(165, 163, 163)")
                .style("font-size", "10px") // all of this are fucked up
                .style("text-align", "center")
                .style("width", "50px") // all of this are fucked up
                .style("height", "40px") // all of this are fucked up
                .style("background", "white")
                .style("color", "#9cb3c3")
                .style("top", 0)
                .style("left", 0)
                .style("display", "none")

            const width = dimensions.w - (dimensions.margins * 2);
            const height = dimensions.h - (dimensions.margins * 2);

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
                .attr("fill", "#78416f")
                .attr("stroke", "#78416f")
                .attr("fill-opacity", 0.2)
                .on("mouseover", (mouseEvent, d) => {
                    d3.select(mouseEvent.target).transition().attr("r", 8)
                    // tooltip.transition().duration(0).style("display", "block")
                    tooltip
                        .style("display", "block")
                        .html(`<div><span>My name is ${d.name}</span></div>`)
                        .style("left", (mouseEvent.pageX + 5) + "px")
                        .style("top", (mouseEvent.pageY - 24) + "px")
                    // const [x,y] = d3.pointer(mouseEvent);
                    // const dataset = d
                    // console.log("i am recognizing gift id " + dataset.id)
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
                            //    " and my index is " + dataset.index +
                                " and name is " + dataset.name)
                })

        // }      
    }, [Data, setDisplayedId])
    console.log(displayedId)
    return (
        <div>
            <Tooltip title="hello world" position="bottom" trigger="click">
            </Tooltip>
            <svg ref={chartRef} width={800} height={500}> {/* need more css here */}
            </svg>
        </div>
    )
}