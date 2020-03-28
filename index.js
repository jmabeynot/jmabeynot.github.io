const color_primary_0 = "#BB8956";	/* Main Primary color */
const color_primary_1 = "#FFE2C4";
const color_primary_2 = "#E3B88C";
const color_primary_3 = "#9B6732";
const color_primary_4 = "#714212";

const color_secondary_1_0 = "#434F80";	/* Main Secondary color (1) */
const color_secondary_1_1 = "#949CBB";
const color_secondary_1_2 = "#66719B";
const color_secondary_1_3 = "#2B3769";
const color_secondary_1_4 = "#141F4D";

const color_secondary_2_0 = "#408B56";	/* Main Secondary color (2) */
const color_secondary_2_1 = "#99C7A7";
const color_secondary_2_2 = "#68A87B";
const color_secondary_2_3 = "#25733D";
const color_secondary_2_4 = "#0D5323";

const color_complement_0 = "#386775";	/* Main Complement color */
const color_complement_1 = "#87A6AE";
const color_complement_2 = "#59828D";
const color_complement_3 = "#225360";
const color_complement_4 = "#0D3A46";

new Vue({
  el: '#app',
  data: function(){
    return {
      options: {
        afterLoad: this.afterLoad,
        navigation: true,
        autoScrolling: false,
        fitToSection: false,
        recordHistory: false,
        anchors: ['page1', 'page2', 'page3'],
        sectionsColor: [
          color_secondary_1_0,
          color_primary_0,
          color_secondary_2_0,
          color_complement_0,
          color_primary_1,
          color_secondary_2_2,
          color_secondary_1_2,
        ]
      },
    }
  },
  methods: {
    afterLoad: function(origin, destination, direction){
      console.log("After load....");
      console.log(destination);
    },
    addSection: function(e) {
      var newSectionNumber = document.querySelectorAll('.fp-section').length + 1

      // creating the section div
      var section = document.createElement('div')
      section.className = 'section'
      section.innerHTML = `<h3>Section ${newSectionNumber}</h3>`

      // adding section
      document.querySelector('#fullpage').appendChild(section)

      // creating the section menu element
      var sectionMenuItem = document.createElement('li')
      sectionMenuItem.setAttribute('data-menuanchor', 'page' + newSectionNumber)
      sectionMenuItem.innerHTML = `<a href="#page${newSectionNumber}">Section${newSectionNumber}</a>`

      // adding anchor for the section
      this.options.anchors.push(`page${newSectionNumber}`)

      // we have to call `update` manually as DOM changes won't fire updates
      // requires the use of the attribute ref="fullpage" on the
      // component element, in this case, <full-page>
      // ideally, use an ID element for that element too
      this.$refs.fullpage.build()
    },

    removeSection: function(){
      var sections = document.querySelector('#fullpage').querySelectorAll('.fp-section')
      var lastSection = sections[sections.length - 1]

      // removing the last section
      lastSection.parentNode.removeChild(lastSection)

      // removing the last anchor
      this.options.anchors.pop()

      // removing the last item on the sections menu
      var sectionsMenuItems = document.querySelectorAll('#menu li')
      var lastItem = sectionsMenuItems[sectionsMenuItems.length - 1]
      lastItem.parentNode.removeChild(lastItem)
    },
  }
});
