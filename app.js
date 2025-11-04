/*
 * Main JavaScript file for the Compassionate Care website.
 *
 * This script defines our React components using the UMD builds of
 * React and ReactDOM. The parallax effect is provided by the
 * `react-parallax` library, which exposes its components on the
 * `window['react-parallax']` namespace after loading. We also use
 * Leaflet to render a small interactive map highlighting the areas
 * served by the business. Because this page is bundled without a
 * build step, all components are created with `React.createElement`
 * instead of JSX.
 */

(function () {
  const { useEffect, useRef, useState } = React;
  // The parallax components are attached to the global object.  We
  // assign them here for convenience.  If the library fails to load
  // (for example without network access) the parallax effect will
  // gracefully degrade because Parallax will be undefined.
  const ParallaxLib = window['react-parallax'] || {};
  const Parallax = ParallaxLib.Parallax || function ({ children }) {
    // fallback: render children directly if Parallax is not available
    return React.createElement(React.Fragment, null, children);
  };

  /*
   * HamburgerMenu component
   *
   * Displays a three‑line “hamburger” icon that toggles into an X
   * when clicked.  When open, a side navigation panel slides out
   * containing links to the various sections of the page.  The
   * transformation from a hamburger to an X gives the user a clear
   * visual indication of the menu state【995805708329959†L93-L96】.
   */
  function HamburgerMenu() {
    const [open, setOpen] = useState(false);

    // When the menu state changes, toggle a class on the document body
    // that allows us to animate the page sliding horizontally when
    // the navigation drawer is open.  Without this effect the menu
    // would simply overlay the content instead of pushing it aside.
    useEffect(
      function () {
        if (open) {
          document.body.classList.add('menu-open');
        } else {
          document.body.classList.remove('menu-open');
        }
      },
      [open]
    );
    const sections = [
      { id: 'about', label: 'About' },
      { id: 'services', label: 'Services' },
      { id: 'map', label: 'Map' },
      { id: 'testimonials', label: 'Testimonials' },
      { id: 'contact', label: 'Contact' },
    ];
    function handleToggle() {
      setOpen(!open);
    }
    function handleLinkClick() {
      // Close the menu after navigation
      setOpen(false);
    }
    return React.createElement(
      React.Fragment,
      null,
      // Main hamburger icon.  Clicking toggles the side menu.
      React.createElement(
        'div',
        {
          className: open ? 'hamburger active' : 'hamburger',
          onClick: handleToggle,
          role: 'button',
          'aria-label': 'Toggle navigation menu',
          'aria-expanded': open,
        },
        [
          React.createElement('span', { className: 'hamburger-line line1', key: 'l1' }),
          React.createElement('span', { className: 'hamburger-line line2', key: 'l2' }),
          React.createElement('span', { className: 'hamburger-line line3', key: 'l3' }),
        ]
      ),
      // Sliding side menu.  When open, it covers the viewport and
      // displays navigation links, a close button and decorative
      // hearts.  Items inside the array are ordered so that the
      // close button appears at the top of the drawer, followed by
      // the navigation links and then the heart container.
      React.createElement(
        'div',
        { className: open ? 'side-menu open' : 'side-menu' },
        [
          // Close button.  Provides an explicit control to dismiss
          // the menu without relying solely on the hamburger icon.
          React.createElement(
            'button',
            {
              className: 'close-button',
              onClick: handleToggle,
              'aria-label': 'Close navigation menu',
              key: 'close-btn',
            },
            '×'
          ),
          // Navigation links
          sections.map(function (sec) {
            return React.createElement(
              'a',
              {
                key: sec.id,
                href: '#' + sec.id,
                onClick: handleLinkClick,
              },
              sec.label
            );
          }),
          // Animated pastel hearts that gently float up through the
          // menu.  Their behaviour is defined in CSS.  A separate
          // container ensures the hearts do not interfere with
          // pointer events on the menu itself.
          React.createElement(
            'div',
            { className: 'heart-container', key: 'heart-container' },
            [
              React.createElement('span', { className: 'heart', key: 'heart1' }),
              React.createElement('span', { className: 'heart', key: 'heart2' }),
              React.createElement('span', { className: 'heart', key: 'heart3' }),
              React.createElement('span', { className: 'heart', key: 'heart4' }),
              React.createElement('span', { className: 'heart', key: 'heart5' }),
            ]
          ),
        ]
      )
    );
  }

  /* Hero section component
   * Displays the main title and tagline on top of a parallax
   * background.  The flower image is included in the `assets` folder
   * and referenced directly in the `bgImage` prop.
   */
  function Hero() {
    return React.createElement(
      Parallax,
      {
        bgImage: 'new_bg1.png',
        strength: 400,
      },
      React.createElement(
        'div',
        { className: 'section hero parallax-section', id: 'home' },
        React.createElement(
          'div',
          { className: 'overlay' },
          // Display only the logo and tagline.  The main heading has
          // been removed to avoid repeating “Compassionate Care”
          // because the logo artwork already includes the company
          // name.  The logo has a transparent background so it
          // blends seamlessly with the overlay panel.
          React.createElement('img', { src: 'logo_no_bg.png', alt: 'Compassionate Care logo', className: 'hero-logo' }),
          React.createElement(
            'p',
            { className: 'hero-tagline' },
            'Providing compassionate home health care services'
          )
        )
      )
    );
  }

  /* About section
   * Summarises the organisation’s mission and coverage area.  The
   * content is adapted from the provided flyer.
   */
  function AboutSection() {
    return React.createElement(
      'section',
      { className: 'section about parallax-section', id: 'about' },
      React.createElement(
        'div',
        { className: 'parallax-overlay' },
        React.createElement('h2', null, 'About Us'),
        React.createElement(
          'p',
          null,
          'Compassionate Care is a family owned home health agency that strives to provide your loved one with nothing but the best home health care to compliment their independent living.'
        ),
        React.createElement(
          'p',
          null,
          'We are an organization committed to serving the needs of our clients and their caregivers.'
        ),
        React.createElement(
          'p',
          null,
          'We cover the following counties in California: Yolo and Solano. In addition, we proudly extend our services to families in Colorado and Washington.'
        )
      )
    );
  }

  /* Services section
   * Lists the services offered by Compassionate Care.  Each item
   * includes a short description.
   */
  function ServicesSection() {
    // Define our services as an array of objects.  This makes it easy
    // to update or extend the list later on.
    const services = [
      {
        title: 'Meal Preparation',
        text: 'Our caregivers are available to prepare hot and well‑balanced nutritional meals for our clients.',
      },
      {
        title: 'Companionship',
        text: 'Engaging in conversation or even sharing a sit down meal is very beneficial to our clients and their happiness.',
      },
      {
        title: 'Light Housekeeping',
        text: 'Housekeeping services include dusting, vacuuming, sweeping, taking out the trash and cleaning the bathroom.',
      },
      {
        title: 'Incidental Transportation',
        text: 'Transportation to medical appointments, beauty salons, barbershops, grocery shopping or anywhere else your loved one would like to go.',
      },
      {
        title: 'Medication Reminders',
        text: 'Our caregivers can remind and assist the client when it’s time to take their medication.',
      },
      {
        title: 'Hospice Care',
        text: 'Our staff is trained in compassion and care for the terminally ill.',
      },
    ];
    return React.createElement(
      'section',
      { className: 'section services parallax-section', id: 'services' },
      React.createElement(
        'div',
        { className: 'parallax-overlay' },
        React.createElement('h2', null, 'Services We Offer'),
        React.createElement(
          'ul',
          null,
          services.map(function (service, index) {
            return React.createElement(
              'li',
              { key: index },
              React.createElement('strong', null, service.title + ': '),
              service.text
            );
          })
        )
      )
    );
  }

  /* Map section
   * Utilises Leaflet to render a small interactive map.  We add
   * markers for Yolo and Solano counties in California, as well as
   * a central marker for Colorado to illustrate the service area.
   */
  function MapSection() {
    const mapRef = useRef(null);
    useEffect(() => {
      // Only initialise the map once the DOM node is available.
      if (!mapRef.current) return;
      // Initialise the map centred over the western United States.  A lower zoom
      // level reveals multiple states at once.
      const map = L.map(mapRef.current).setView([40.0, -112.0], 4);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(map);

      // Draw the served states using more realistic polygon boundaries instead
      // of simple rectangular bounding boxes.  The coordinate arrays below
      // were extracted from the official Leaflet choropleth example and are
      // simplified outlines for California, Colorado and Washington.  Using
      // polygons makes the service area look much cleaner and avoids the
      // obvious square borders of a bounding box.

      const stateStyle = {
        color: '#a353c5',
        weight: 1,
        fillColor: '#d8afe8',
        fillOpacity: 0.25,
      };

      // California outline (single polygon).  Coordinates are ordered
      // clockwise and represent the outer boundary of the state.
      const californiaCoords = [
        [42.006186, -123.233256],
        [42.011663, -122.378853],
        [41.995232, -121.037003],
        [41.995232, -120.001861],
        [40.264519, -119.996384],
        [38.999346, -120.001861],
        [38.101128, -118.71478],
        [37.21934, -117.498899],
        [36.501861, -116.540435],
        [35.970598, -115.85034],
        [35.00118, -114.634459],
        [34.87521, -114.634459],
        [34.710902, -114.470151],
        [34.448009, -114.333228],
        [34.174162, -114.256551],
        [34.108438, -114.415382],
        [33.933176, -114.535874],
        [33.697668, -114.497536],
        [33.54979, -114.524921],
        [33.40739, -114.727567],
        [33.034958, -114.661844],
        [33.029481, -114.524921],
        [32.843265, -114.470151],
        [32.755634, -114.524921],
        [32.717295, -114.72209],
        [32.624187, -116.04751],
        [32.536556, -117.126467],
        [32.668003, -117.24696],
        [32.876127, -117.252437],
        [33.122589, -117.329114],
        [33.297851, -117.471515],
        [33.538836, -117.7837],
        [33.763391, -118.183517],
        [33.703145, -118.260194],
        [33.741483, -118.413548],
        [33.840068, -118.391641],
        [34.042715, -118.566903],
        [33.998899, -118.802411],
        [34.146777, -119.218659],
        [34.26727, -119.278905],
        [34.415147, -119.558229],
        [34.40967, -119.875891],
        [34.475393, -120.138784],
        [34.448009, -120.472878],
        [34.579455, -120.64814],
        [34.858779, -120.609801],
        [34.902595, -120.670048],
        [35.099764, -120.631709],
        [35.247642, -120.894602],
        [35.450289, -120.905556],
        [35.461243, -121.004141],
        [35.636505, -121.168449],
        [35.674843, -121.283465],
        [35.784382, -121.332757],
        [36.195153, -121.716143],
        [36.315645, -121.896882],
        [36.638785, -121.935221],
        [36.6114, -121.858544],
        [36.803093, -121.787344],
        [36.978355, -121.929744],
        [36.956447, -122.105006],
        [37.115279, -122.335038],
        [37.241248, -122.417192],
        [37.361741, -122.400761],
        [37.520572, -122.515777],
        [37.783465, -122.515777],
        [37.783465, -122.329561],
        [38.15042, -122.406238],
        [38.112082, -122.488392],
        [37.931343, -122.504823],
        [37.893004, -122.701993],
        [38.029928, -122.937501],
        [38.265436, -122.97584],
        [38.451652, -123.129194],
        [38.566668, -123.331841],
        [38.698114, -123.44138],
        [38.95553, -123.737134],
        [39.032208, -123.687842],
        [39.366301, -123.824765],
        [39.552517, -123.764519],
        [39.831841, -123.85215],
        [40.105688, -124.109566],
        [40.259042, -124.361506],
        [40.439781, -124.410798],
        [40.877937, -124.158859],
        [41.025814, -124.109566],
        [41.14083, -124.158859],
        [41.442061, -124.065751],
        [41.715908, -124.147905],
        [41.781632, -124.257444],
        [42.000709, -124.213628],
        [42.006186, -123.233256]
      ];

      // Colorado outline (single polygon).  Coordinates are ordered clockwise.
      const coloradoCoords = [
        [41.003906, -107.919731],
        [40.998429, -105.728954],
        [41.003906, -104.053011],
        [41.003906, -102.053927],
        [40.001626, -102.053927],
        [36.994786, -102.042974],
        [37.000263, -103.001438],
        [36.994786, -104.337812],
        [36.994786, -106.868158],
        [37.000263, -107.421329],
        [37.000263, -109.042503],
        [38.166851, -109.042503],
        [38.27639, -109.058934],
        [39.125316, -109.053457],
        [40.998429, -109.04798],
        [41.003906, -107.919731]
      ];

      // Washington outline (multi polygon).  The first entry is the mainland
      // boundary, followed by two smaller island polygons off the coast.
      const washingtonCoords = [
        [
          [49.000239, -117.033359],
          [47.762451, -117.044313],
          [46.426077, -117.038836],
          [46.343923, -117.055267],
          [46.168661, -116.92382],
          [45.993399, -116.918344],
          [45.998876, -118.988627],
          [45.933153, -119.125551],
          [45.911245, -119.525367],
          [45.823614, -119.963522],
          [45.725029, -120.209985],
          [45.697644, -120.505739],
          [45.746937, -120.637186],
          [45.604536, -121.18488],
          [45.670259, -121.217742],
          [45.725029, -121.535404],
          [45.708598, -121.809251],
          [45.549767, -122.247407],
          [45.659305, -122.762239],
          [45.960537, -122.811531],
          [46.08103, -122.904639],
          [46.185092, -123.11824],
          [46.174138, -123.211348],
          [46.146753, -123.370179],
          [46.261769, -123.545441],
          [46.300108, -123.72618],
          [46.239861, -123.874058],
          [46.327492, -124.065751],
          [46.464416, -124.027412],
          [46.535616, -123.895966],
          [46.74374, -124.098612],
          [47.285957, -124.235536],
          [47.357157, -124.31769],
          [47.740543, -124.427229],
          [47.88842, -124.624399],
          [48.184175, -124.706553],
          [48.381345, -124.597014],
          [48.288237, -124.394367],
          [48.162267, -123.983597],
          [48.167744, -123.704273],
          [48.118452, -123.424949],
          [48.167744, -123.162056],
          [48.080113, -123.036086],
          [48.08559, -122.800578],
          [47.866512, -122.636269],
          [47.882943, -122.515777],
          [47.587189, -122.493869],
          [47.318818, -122.422669],
          [47.346203, -122.324084],
          [47.576235, -122.422669],
          [47.800789, -122.395284],
          [48.030821, -122.230976],
          [48.123929, -122.362422],
          [48.288237, -122.373376],
          [48.468976, -122.471961],
          [48.600422, -122.422669],
          [48.753777, -122.488392],
          [48.775685, -122.647223],
          [48.8907, -122.795101],
          [49.000239, -122.756762],
          [49.000239, -117.033359]
        ],
        [
          [48.310145, -122.718423],
          [48.35396, -122.586977],
          [48.151313, -122.608885],
          [48.227991, -122.767716],
          [48.310145, -122.718423]
        ],
        [
          [48.583992, -123.025132],
          [48.715438, -122.915593],
          [48.556607, -122.767716],
          [48.419683, -122.811531],
          [48.458022, -123.041563],
          [48.583992, -123.025132]
        ]
      ];

      // Helper to create polygons or multipolygons from coordinate lists.
      function drawPolygon(coordList) {
        // Leaflet expects [lat, lng] pairs.  Our arrays are [lat, lng] already.
        return L.polygon(coordList, stateStyle).addTo(map);
      }
      drawPolygon(californiaCoords);
      drawPolygon(coloradoCoords);
      // Washington is a multipolygon, so draw each part separately
      washingtonCoords.forEach(function (poly) {
        drawPolygon(poly);
      });

      // Add specific markers within the states for key service areas
      const markers = [
        {
          coords: [38.8339, -104.8214],
          label: 'Colorado Springs, CO',
        },
        {
          coords: [36.6002, -121.8947],
          label: 'Monterey County, CA',
        },
        {
          coords: [47.6062, -122.3321],
          label: 'King County, WA',
        },
      ];
      markers.forEach(function (m) {
        L.marker(m.coords).addTo(map).bindPopup(m.label);
      });

      // Clean up on unmount
      return function cleanup() {
        map.remove();
      };
    }, []);
    return React.createElement(
      'section',
      { className: 'section map-section parallax-section', id: 'map' },
      React.createElement(
        'div',
        { className: 'parallax-overlay' },
        [
          React.createElement('h2', { key: 'heading' }, 'Areas We Serve'),
          React.createElement('div', { className: 'map-container', ref: mapRef, key: 'map' }),
          // Provide a brief list of regional home offices below the map.
          React.createElement(
            'p',
            { className: 'map-offices', key: 'offices' },
            'Home offices located in King County, Colorado Springs, and Monterey Bay.'
          ),
        ]
      )
    );
  }

  /* Testimonials section
   * Presents a few fictional testimonials to illustrate client
   * satisfaction.  We reuse the cropped photograph from the flyer
   * as the first client image for familiarity.  Additional images
   * could be added as desired.
   */
  function TestimonialsSection() {
    const testimonials = [
      {
        img: 'woman_1.jpg',
        quote: 'Compassionate Care has been a blessing for our family. Their caregivers are friendly and professional.',
        name: 'Mary K., Daughter',
      },
      {
        img: 'woman_2.jpg',
        quote: 'The service they provide gives me peace of mind knowing my mom is taken care of.',
        name: 'Eleanor S. Client',
      },
      {
        img: 'woman_3.jpg',
        quote: 'I love how attentive and caring the staff are they treat clients like family.',
        name: 'Linda T., Client',
      },
    ];
    return React.createElement(
      'section',
      { className: 'section testimonials parallax-section', id: 'testimonials' },
      React.createElement(
        'div',
        { className: 'parallax-overlay' },
        React.createElement('h2', null, 'Testimonials'),
        React.createElement(
          'div',
          { className: 'testimonial-grid' },
          testimonials.map(function (t, index) {
            return React.createElement(
              'div',
              { className: 'testimonial-card', key: index },
              React.createElement('img', { src: t.img, alt: t.name + ' photo' }),
              React.createElement('p', null, '"' + t.quote + '"'),
              React.createElement('span', null, t.name)
            );
          })
        )
      )
    );
  }

  /* Contact section
   * Displays contact information and a simple form.  The form is
   * non‑functional and included purely for aesthetics.  In a real
   * production environment the form would submit to a server or
   * service such as Formspree or Netlify Forms.
   */
  function ContactSection() {
    // Contact form state and submission handler
    const [status, setStatus] = useState(null);
    function handleSubmit(e) {
      e.preventDefault();
      const formData = new FormData(e.target);
      const payload = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        message: formData.get('message'),
      };
      setStatus('sending');
      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          if (res.ok) {
            setStatus('success');
            e.target.reset();
          } else {
            setStatus('error');
          }
        })
        .catch(function () {
          setStatus('error');
        });
    }
    return React.createElement(
      'section',
      { className: 'section contact parallax-section', id: 'contact' },
      React.createElement(
        'div',
        { className: 'parallax-overlay' },
        React.createElement('h2', null, 'Contact Us'),
        React.createElement(
          'div',
          { className: 'contact-info' },
          React.createElement('p', null, 'Phone: ', React.createElement('a', { href: 'tel:5303416155' }, '(530) 341-6155')),
          React.createElement('p', null, 'Email: ', React.createElement('a', { href: 'mailto:compassionatecare8@icloud.com' }, 'compassionatecare8@icloud.com'))
        ),
        React.createElement(
          'form',
          { onSubmit: handleSubmit },
          React.createElement('input', { type: 'text', name: 'name', placeholder: 'Your Name', required: true }),
          React.createElement('input', { type: 'email', name: 'email', placeholder: 'Your Email', required: true }),
          React.createElement('input', { type: 'tel', name: 'phone', placeholder: 'Your Phone Number' }),
          React.createElement('textarea', { name: 'message', rows: '4', placeholder: 'Your Message', required: true }),
          React.createElement('button', { type: 'submit' }, status === 'sending' ? 'Sending...' : 'Send Message')
        ),
        status === 'success'
          ? React.createElement('p', { style: { color: '#4b0f75', marginTop: '10px' } }, 'Thank you for reaching out!')
          : status === 'error'
          ? React.createElement('p', { style: { color: 'red', marginTop: '10px' } }, 'An error occurred. Please try again later.')
          : null
      )
    );
  }

  /* Main application component */
  function App() {
    return React.createElement(
      React.Fragment,
      null,
      React.createElement(HamburgerMenu),
      React.createElement(Hero),
      React.createElement(AboutSection),
      React.createElement(ServicesSection),
      React.createElement(MapSection),
      React.createElement(TestimonialsSection),
      React.createElement(ContactSection)
    );
  }

  // ScrollSpy component is no longer needed now that we use a hamburger
  // dropdown menu for navigation.

  // Finally render the application into the root element
  ReactDOM.createRoot(document.getElementById('root')).render(
    React.createElement(App)
  );
})();